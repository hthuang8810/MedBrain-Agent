import os
import subprocess
import json
import soundfile as sf
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
import uvicorn
from vosk import KaldiRecognizer
from model.model_management import MyModel
from Agent.chat_agent import ChatAgent, more_speak
from Agent.login_agent import more_speak_login
from Agent.chat_agent_patient import ChatAgentPatient, more_speak_patient
from tool.sql_service import sql_tool_pool, pool as mysql_pool
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import redis
from dotenv import load_dotenv


load_dotenv()

# 链接Redis数据库
client = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PASSWORD"), protocol=2)

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


# 定义参数对象
class ChatArgs(BaseModel):
    questions: str  = Field(..., description="问题")
    userId: str = Field(..., description="会话ID列表")
@app.post("/chat")
async def chat_stream(args: ChatArgs):
    """SSE 流式聊天端点"""
    async def event_generator():
        try:
            # 根据关键词选择智能体
            if "邮箱" in args.questions:
                agent_obj = ChatAgentPatient()
            else:
                agent_obj = ChatAgent()

            agent = agent_obj.get_agent()
            config = {"configurable": {"session_id": args.userId}}

            # 使用 LangChain astream_events 逐 token 流式输出（含工具调用状态）
            async for event in agent.astream_events(
                {"input": args.questions}, config, version="v1"
            ):
                ev = event.get("event")
                if ev == "on_chat_model_stream":
                    chunk = event["data"].get("chunk")
                    if chunk is not None:
                        token = getattr(chunk, "content", None)
                        if isinstance(token, str) and token:
                            # 逐 token 下发，前端可实现打字机效果
                            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
                elif ev == "on_tool_start":
                    # 工具调用状态，前端可提示"正在查询..."
                    name = event.get("name")
                    if name:
                        yield f"data: {json.dumps({'tool': name}, ensure_ascii=False)}\n\n"
            # 流结束信号
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

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
@app.post("/speech_to_text")
async def speech_to_text(file: UploadFile = File(...)):
    try:
        # === Step 1. 保存上传文件到磁盘 ===
        input_path = "temp_input.webm"
        output_path = "temp_fixed.wav"

        with open(input_path, "wb") as f:
            f.write(await file.read())

        # === Step 2. 使用 ffmpeg 转换为 16kHz 单声道 wav ===
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
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