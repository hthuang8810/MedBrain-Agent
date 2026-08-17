from pydantic import BaseModel,Field
from langchain.tools import tool
from fastmcp import Client
import asyncio

class MySQLArgs(BaseModel):
    query: str = Field(..., description="sql语句")
@tool(args_schema=MySQLArgs)
def sql_tool_pool(query: str)->str:
    """
    执行sql语句
    """
    async def run_sql_tool():
        async with Client("http://localhost:8008/sse") as client:
            rs = await client.call_tool("sql_tool_pool", {"query": query})
            return rs
    return asyncio.run(run_sql_tool())