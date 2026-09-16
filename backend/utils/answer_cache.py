"""回答缓存。

只用于「会话历史为空」的轮次：此时 prompt 仅由 system + 本轮问题构成，
答案只取决于问题文本，用全局 key 才是可靠的。带历史的轮次既不读也不写
缓存（同一句话在不同上下文里指代可能不同）。

调用方还需保证本轮没有触发副作用工具（发邮件 / 生成文档），否则缓存住
「已发送」这类回答会导致下次只重放文本、并不真的执行。
"""

import hashlib

from utils.redis_client import client

# 改动 chat_agent.py 的 system prompt 或工具集时递增此版本号，
# 否则旧 key 下缓存的答案会和新 prompt 的语义混在一起。
PROMPT_VERSION = "v2"

CACHE_TTL = 3600  # 秒
_KEY_PREFIX = "chat:cache:"


def _make_key(question: str) -> str:
    # strip() 归一化，让 "你好" 和 "你好 " 共用一条缓存
    digest = hashlib.sha256(question.strip().encode("utf-8")).hexdigest()
    return f"{_KEY_PREFIX}{PROMPT_VERSION}:{digest}"


def get_answer(question: str) -> str | None:
    """读取缓存。任何异常都视作未命中，绝不向请求路径抛出。"""
    try:
        raw = client.get(_make_key(question))
        return raw.decode("utf-8") if raw else None
    except Exception as e:
        print("读取回答缓存失败：", e)
        return None


def set_answer(question: str, answer: str) -> None:
    """写入缓存。任何异常都吞掉 —— 缓存写失败不能影响正常回复。"""
    if not answer:
        return
    try:
        client.set(_make_key(question), answer, ex=CACHE_TTL)
    except Exception as e:
        print("写入回答缓存失败：", e)
