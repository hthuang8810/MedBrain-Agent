import os
import redis
from dotenv import load_dotenv

load_dotenv()

# 全局唯一的 Redis 客户端。
#
# 之前三处各建各的：main.py 读 .env，而 inMemoryHistory_redis.py 与 chat_agent.py
# 硬编码 localhost 且不读 REDIS_PASSWORD —— 一旦 Redis 开了鉴权，会话历史会挂掉
# 而验证码功能却照常，极难排查。统一到这里。
#
# decode_responses 必须保持 False（默认值）：main.py 的验证码逻辑依赖 bytes，
# 形如 client.get(email).decode()，改成 True 会抛 AttributeError。
#
# socket_timeout 防止 Redis 无响应时无限阻塞事件循环（此前没有任何超时设置）。
client = redis.Redis(
    host=os.getenv("REDIS_HOST") or "localhost",
    port=int(os.getenv("REDIS_PORT") or 6379),
    password=os.getenv("REDIS_PASSWORD") or None,
    db=int(os.getenv("REDIS_DB") or 0),
    protocol=2,  # RESP2：兼容 Redis<6，避免 HELLO 命令
    decode_responses=False,
    socket_timeout=5,
)
