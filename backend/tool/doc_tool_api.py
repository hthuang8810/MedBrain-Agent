# agent/doc_tool_pool.py
from langchain.tools import tool
from pydantic import BaseModel, Field
from fastmcp import Client
import asyncio


# 参数模型
class DocArgs(BaseModel):
    content: str = Field(..., description="报告内容")
    title: str = Field("医疗报告", description="报告标题")
    doc_type: str = Field("word", description="生成文档类型，可选：word 或 pdf")


@tool(args_schema=DocArgs)
def doc_tool_pool(content: str, title: str = "医疗报告", doc_type: str = "word") -> str:
    """
    调用 MCP 文档生成工具（doc_tool）以生成 Word 或 PDF 报告
    """
    async def run():
        # 连接到 MCP 服务端（保持端口和 mcp_tool/doc_tool_mcp.py 一致）
        async with Client("http://localhost:8008/sse") as client:
            rs = await client.call_tool(
                "generate_word_tool",  # MCP 端注册的工具名称
                {"content": content, "title": title, "doc_type":doc_type}
            )
            return rs.data

    return asyncio.run(run())
