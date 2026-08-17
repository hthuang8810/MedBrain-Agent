from pydantic import BaseModel, Field # 输入参数验证
from dotenv import load_dotenv
from langchain.tools import tool
from fastmcp import Client
import asyncio

load_dotenv()

class FAISToolArgs(BaseModel):
    # FAISS向量数据库查询， Field (...，description 描述 -> 智能体需要根据描述进行参数填写)
    query: str = Field(..., description="FAISS向量数据库查询")
@tool(args_schema=FAISToolArgs)
def faiss_tool(query:str)->str:
    """
    执行FAISS向量数据库查询
    """
    try:
        async def run_faiss() -> str:
            async with Client("http://localhost:8008/sse") as client:
                rs = await client.call_tool("faiss_tool", {"query": query})
                return rs
        return asyncio.run(run_faiss())
    except Exception as e:
        print("执行异常：",e)
        return "FAISS向量数据库查询失败"