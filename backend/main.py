import shutil
import subprocess
import json
import asyncio
from collections import defaultdict
import soundfile as sf
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
import uvicorn
from vosk import KaldiRecognizer
from langchain_core.messages import HumanMessage, AIMessage
from model.model_management import MyModel
from Agent.chat_agent import ChatAgent
from Agent.login_agent import more_speak_login
from tool.sql_service import sql_tool_pool, pool as mysql_pool
from utils.inMemoryHistory_redis import get_session_history
from utils.answer_cache import get_answer, set_answer
from utils.redis_client import client
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


load_dotenv()

# 创建一个FastAPI应用实例
app = FastAPI(title="基于FastAPI+langchain+Agent的医疗系统",description="医疗助手",version="0.1.0")
# ======== 允许跨域的配置部分 ========
# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 开发阶段允许所有来源（生产环境改为具体域名）
    allow_credentials=False,  # 项目不依赖cookie，关闭以支持通配符Origin
    allow_methods=["*"],      # 允许所有方法：GET, POST, PUT, DELETE...
    allow_headers=["*"],      # 允许所有请求头
)


# 只读工具白名单：名单之外的工具一律视为有副作用，不写缓存。
# 用白名单而非黑名单 —— 将来新增工具时默认走保守分支（发邮件的代价远高于少缓存一条）。
READ_ONLY_TOOLS = {"sql_tool_pool", "neo4j_tool_pool", "faiss_tool", "amap_tool"}

# 可缓存答案的最小长度，滤掉空回复和"好的"这类寒暄
MIN_CACHEABLE_LEN = 8

# 每个会话一把锁，串行化同一会话的并发请求。
# 同时修掉 RedisChatHistory.add_messages 的 read-modify-write 丢消息问题
# （两个请求同时读改写同一个历史键）。当前是单进程 uvicorn，进程内锁足够。
_session_locks = defaultdict(asyncio.Lock)


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _chunk_text(text: str, size: int = 24):
    """把长文本切片下发，让缓存命中同样有打字机效果（前端路径无需区分两种来源）"""
    for i in range(0, len(text), size):
        yield text[i:i + size]


def _merged_message(output):
    """取出 stream/end 事件里的消息对象，兼容 v1 与 v2 的两种形态。

    v1 是 LLMResult 风格的 dict，v2 直接给 AIMessageChunk。
    """
    if isinstance(output, dict):
        try:
            return output["generations"][0][0]["message"]
        except (KeyError, IndexError, TypeError):
            return None
    return output


def _final_answer_from_event(data) -> str | None:
    """从 on_chain_end 的输出里取最终答案。

    根事件（RunnableWithMessageHistory）的 output 是 AgentExecutor 合并出的
    AddableDict，形如 {'output': '...', 'messages': [...], 'steps': [...]}，
    其中 output 正是被写进会话历史的那个字符串 —— 语义上就该缓存它。
    取不到时返回 None，调用方会回退到会话历史里的最后一条 AIMessage。
    """
    out = data.get("output") if isinstance(data, dict) else None
    if isinstance(out, dict) and isinstance(out.get("output"), str):
        return out["output"]
    return None


async def _run_turn(question: str, session_id: str):
    """跑完一轮对话并逐条下发 SSE 数据。"""
    # 会话历史为空时，答案只取决于问题文本，全局 key 才可靠。
    # 这里失败不能让整个请求挂掉 —— fail open 到"本轮不用缓存"。
    try:
        history_empty = len(get_session_history(session_id).messages) == 0
    except Exception as e:
        print("读取会话历史失败，本轮不使用缓存：", e)
        history_empty = False

    if history_empty:
        cached = get_answer(question)
        if cached is not None:
            # 命中时不会触发 RunnableWithMessageHistory 的历史写入，
            # 必须手工补上这一轮，否则下一轮模型会以为历史是空的。
            try:
                get_session_history(session_id).add_messages([
                    HumanMessage(content=question),
                    AIMessage(content=cached),
                ])
            except Exception as e:
                print("缓存命中时补写会话历史失败：", e)
            for piece in _chunk_text(cached):
                yield _sse({"token": piece})
            yield _sse({"done": True})
            return

    agent = ChatAgent().get_agent()
    config = {"configurable": {"session_id": session_id}}

    side_effect = False           # 本轮是否调用了有副作用的工具
    tool_error = False            # 是否有工具抛错
    last_had_tool_calls = False   # 最后一次模型输出是否还想调工具（= 被强制截断，不是真答案）
    final_answer = None

    # 使用 LangChain astream_events 逐 token 流式输出（含工具调用状态）
    async for event in agent.astream_events(
        {"input": question}, config, version="v2"
    ):
        ev = event.get("event")
        data = event.get("data") or {}
        if ev == "on_chat_model_stream":
            token = getattr(data.get("chunk"), "content", None)
            if isinstance(token, str) and token:
                # 逐 token 下发，前端可实现打字机效果
                yield _sse({"token": token})
        elif ev == "on_tool_start":
            # 工具调用状态，前端可提示"正在查询..."
            name = event.get("name")
            if name:
                if name not in READ_ONLY_TOOLS:
                    side_effect = True
                yield _sse({"tool": name})
        elif ev == "on_tool_error":
            tool_error = True
        elif ev == "on_chat_model_end":
            msg = _merged_message(data.get("output"))
            last_had_tool_calls = bool(getattr(msg, "tool_calls", None))
        elif ev == "on_chain_end":
            answer = _final_answer_from_event(data)
            if answer is not None:
                final_answer = answer

    if final_answer is None and history_empty:
        # 回退：本轮已被写进会话历史，取最后一条 AI 消息
        try:
            for m in reversed(get_session_history(session_id).messages):
                if isinstance(m, AIMessage):
                    final_answer = m.content
                    break
        except Exception as e:
            print("回退读取最终答案失败：", e)

    # 不放在 finally 里：客户端中途断开会关闭生成器，
    # 此时答案可能只攒了一半，缓存它是错的。
    if (history_empty and not side_effect and not tool_error
            and not last_had_tool_calls
            and final_answer and len(final_answer.strip()) >= MIN_CACHEABLE_LEN):
        set_answer(question, final_answer)

    yield _sse({"done": True})


# 定义参数对象
class ChatArgs(BaseModel):
    questions: str = Field(..., description="问题")
    sessionId: str = Field(..., description="会话ID，前端用 {userId}:{chatId} 组合而成")
@app.post("/chat")
async def chat_stream(args: ChatArgs):
    """SSE 流式聊天端点"""
    async def event_generator():
        try:
            # 同一会话串行执行，避免并发请求互相覆盖 Redis 历史
            async with _session_locks[args.sessionId]:
                async for chunk in _run_turn(args.questions, args.sessionId):
                    yield chunk
        except Exception as e:
            yield _sse({"error": str(e)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        # 防反向代理缓冲整个流，否则打字机效果失效
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

# 定义一个登录请求参数
class LoginArgs(BaseModel):
    userName: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
@app.post("/login")
def login(args: LoginArgs):
    try:
        # 获取请求参数
        userName = args.userName
        password = args.password
        sql = "SELECT user_id FROM user_info WHERE user_name=%s AND password=%s"
        params =  (userName, password)
        rs = sql_tool_pool(sql, params)
        # rs 是结果元组列表；查询出错时 sql_tool_pool 会返回字符串 "sql执行失败"
        if isinstance(rs, list) and rs:
            # 获取登录用的userId的值
            user_id = rs[0][0]
            d = {"code": 200, "data": user_id, "msg": "登录成功"}
        else:
            d = {"code": 500, "data": "用户名或密码错误", "msg": "error"}
        return d
    except Exception as e:
        print("异常错误", e)
        return {"code": 500, "data": "error", "msg": "error"}


# ======== 数据库依赖注入 ========
def get_db():
    """每个请求获取独立连接，请求结束后归还连接池"""
    conn = mysql_pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()

# 定义注册请求参数
class RegisterArgs(BaseModel):
    userName: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    email: str = Field("", description="邮箱")
@app.post("/register")
def register(args: RegisterArgs, conn=Depends(get_db)):
    try:
        cursor = conn.cursor()
        # 检查用户名是否已存在
        cursor.execute("SELECT user_id FROM user_info WHERE user_name=%s", (args.userName,))
        if cursor.fetchone():
            return {"code": 500, "data": "用户名已存在", "msg": "error"}
        # 检查邮箱是否已被使用
        if args.email:
            cursor.execute("SELECT user_id FROM user_info WHERE email=%s", (args.email,))
            if cursor.fetchone():
                return {"code": 500, "data": "该邮箱已注册", "msg": "error"}
        # 生成 user_id（使用 UUID）
        import uuid
        user_id = str(uuid.uuid4())[:8]
        # 插入新用户
        cursor.execute(
            "INSERT INTO user_info (user_id, user_name, password, email) VALUES (%s, %s, %s, %s)",
            (user_id, args.userName, args.password, args.email),
        )
        conn.commit()
        return {"code": 200, "data": user_id, "msg": "注册成功"}
    except Exception as e:
        print("注册异常错误", e)
        return {"code": 500, "data": "注册失败", "msg": "error"}


# 定义验证码发送参数
class SendCodeArgs(BaseModel):
    email: str = Field(..., description="收件人邮箱")
@app.post("/send_code")
def send_code(args: SendCodeArgs):
    try:
        # 获取用户邮箱
        email = args.email
        # 构建问题
        questions = [
            f"请给邮箱{email}发送一封邮件，主题是: xxxx公司登录验证码，内容:验证码"
        ]
        # 调用邮件智能体
        rs = more_speak_login(questions)
        # 获取验证码
        code = rs[0][:4]
        # 把验证码保存到redis中, 设置有效期
        client.set(email, code, ex=60)
        return {"code": 200, "data": "发送成功", "msg": "success"}
    except Exception as e:
        print("验证码异常错误", e)
        return {"code": 500, "data": "发送失败", "msg": "error"}

# 定义验证码登录验证参数
class CodeVerifyArgs(BaseModel):
    email: str = Field(..., description="收件人邮箱")
    code: str = Field(..., description="验证码")

@app.post("/code_verify")
def code_verify(args: CodeVerifyArgs):
    try:
        # 获取用户邮箱
        email = args.email
        # 获取验证码
        code = args.code
        value = client.get(email).decode()
        # 验证码验证
        if value:
            if value == code:
                return {"code": 200, "data": "验证码登录成功", "msg": "success"}
            else:
                return {"code": 500, "data": "验证码错误", "msg": "error"}
        else:
            return {"code": 500, "data": "验证码已失效", "msg": "error"}
    except Exception as e:
        print("验证码异常错误", e)
        return {"code": 500, "data": "", "msg": "error"}

# 语音识别
VOSK_MODEL = MyModel.get_vosk_model()  # 加载一次模型

# 解析 ffmpeg 可执行文件路径：优先系统 PATH，其次 imageio-ffmpeg 自带的静态二进制
def resolve_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


# 全局解析一次；若两种来源都不可用，给出明确提示
FFMPEG_EXE = resolve_ffmpeg()
if not FFMPEG_EXE:
    print(" 警告：未找到 ffmpeg，语音识别功能不可用，请安装 ffmpeg 或 pip install imageio-ffmpeg")

@app.post("/speech_to_text")
async def speech_to_text(file: UploadFile = File(...)):
    try:
        # === Step 1. 保存上传文件到磁盘 ===
        input_path = "temp_input.webm"
        output_path = "temp_fixed.wav"

        with open(input_path, "wb") as f:
            f.write(await file.read())

        # === Step 2. 使用 ffmpeg 转换为 16kHz 单声道 wav ===
        ffmpeg = FFMPEG_EXE or resolve_ffmpeg()
        if not ffmpeg:
            return {"code": 500, "msg": "服务器缺少 ffmpeg，无法进行语音识别"}
        subprocess.run([
            ffmpeg, "-y", "-i", input_path,
            "-ac", "1", "-ar", "16000",
            output_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # === Step 3. 检查音频信息 ===
        data, samplerate = sf.read(output_path)
        duration = len(data) / samplerate
        print(f" 收到音频: {output_path} ({samplerate}Hz, {duration:.2f}s)")

        if duration < 0.3:
            return {"code": 500, "msg": "录音太短，请重新说一遍"}

        # === Step 4. 初始化识别器 ===
        rec = KaldiRecognizer(VOSK_MODEL, 16000)

        import wave, json
        wf = wave.open(output_path, "rb")
        text = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                text += res.get("text", "")
        text += json.loads(rec.FinalResult()).get("text", "")
        text = text.replace(" ", "")
        wf.close()

        print(" 识别结果：", text)

        if not text.strip():
            return {"code": 500, "msg": "语音识别失败，请重试"}

        return {"code": 200, "data": text, "msg": "success"}

    except Exception as e:
        import traceback
        print(" 语音识别异常：", traceback.format_exc())
        return {"code": 500, "msg": str(e)}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)