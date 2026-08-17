from pydantic import BaseModel,Field
from langchain.tools import tool
from fastmcp import Client
import asyncio

class Neo4jArgs(BaseModel):
    query:str =Field(...,description="cypher语句")
@tool(args_schema=Neo4jArgs)
def neo4j_tool_pool(query:str)->str:
    """
     执行cypher语句
    """
    async def run() -> str:
        async with Client("http://localhost:8008/sse") as client:
            result = await client.call_tool("neo4j_tool", {"query": query})
            return result.data
    return asyncio.run(run())


