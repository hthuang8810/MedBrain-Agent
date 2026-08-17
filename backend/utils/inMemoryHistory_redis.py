from typing import List, Dict
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import redis
import json
# 连接本地 Redis（默认端口 6379）
client = redis.StrictRedis(host='localhost', port=6379, db=0)

# 自己实现一个最简单的内存消息历史
class RedisChatHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, max_history: int = 5):
        self.session_id = session_id
        self.max_history = max_history  # 最大历史消息数量
    @property
    def messages(self) -> List[BaseMessage]:
        """从 Redis 获取消息并反序列化"""
        history_json = client.get(self.session_id)  # 从 Redis 获取历史消息
        if history_json:
            messages_dict = json.loads(history_json)  # 将 JSON 字符串反序列化为字典
            return [self._deserialize_message(msg) for msg in messages_dict]  # 反序列化为消息对象
        return []  # 如果 Redis 中没有历史消息，返回空列表

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """将消息序列化后存储到 Redis"""
        current_history = self.messages  # 获取当前存储的历史消息
        current_history.extend(messages)  # 将新消息添加到历史中
        if len(current_history) > self.max_history:
            current_history = current_history[-self.max_history:]  # 如果超过最大历史数，丢弃最早的消息

        # 序列化消息并存储到 Redis
        serialized_messages = [self._serialize_message(msg) for msg in current_history]
        client.set(self.session_id, json.dumps(serialized_messages))  # 存储到 Redis 中

    def clear(self) -> None:
        """清空 Redis 中的历史记录"""
        client.delete(self.session_id)

    def _serialize_message(self, message: BaseMessage) -> dict:
        """将消息对象序列化为字典"""
        return {
            "type": message.__class__.__name__,  # 获取消息类型（HumanMessage 或 AIMessage）
            "content": message.content,  # 获取消息内容
            "metadata": message.metadata if hasattr(message, "metadata") else None,  # 获取消息的元数据
        }

    def _deserialize_message(self, msg_dict: dict) -> BaseMessage:
        """将字典反序列化为对应的消息对象"""
        message_type = msg_dict["type"]
        if message_type == "HumanMessage":
            return HumanMessage(content=msg_dict["content"], metadata=msg_dict["metadata"])
        elif message_type == "AIMessage":
            return AIMessage(content=msg_dict["content"], metadata=msg_dict["metadata"])
        else:
            raise ValueError(f"Unsupported message type: {message_type}")

# 会话存储器
_store: Dict[str, RedisChatHistory] = {}
def get_session_history(session_id: str) -> RedisChatHistory:
    if session_id not in _store:
        _store[session_id] = RedisChatHistory(session_id=session_id)
    return _store[session_id]
