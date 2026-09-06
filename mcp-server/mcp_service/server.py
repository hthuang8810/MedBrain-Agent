from fastmcp import FastMCP
from email_service.email_service import send_email_tool
from database_service.neo4j_service import neo4j_tool_pool
from database_service.sql_service import sql_tool_pool
from RAG_service.RAG_service import faiss_tool
from amap_service.amap_service import amap_service_tool
from file_service.doc_tool_mcp import generate_word, generate_pdf
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 1.定义mcp应用程序
mcp = FastMCP(
    name="mcp服务",
    version="0.1.0",
)

# 2.定义mcp工具

@mcp.tool(name="neo4j_tool",description="neo4j工具,执行cypher语句")
def neo4j_tool(query: str) -> str:
    """
    cypher语句查询
    :param query: cypher语句
    :return: 答案
    """
    rs = neo4j_tool_pool(query)
    return rs

@mcp.tool(name="sql_tool_pool",description="sql工具,执行sql语句")
def sql_tool(query: str) -> str:
    """
    sql语句查询
    :param query: sql语句
    :return: 答案
    """
    rs = sql_tool_pool(query)
    return rs

@mcp.tool(name="send_email_tool",description="邮件发送工具")
def send_email(to_email: str, content: str, subject: str) -> str:
    """
    邮件发送
    :param to_email: 收件人邮箱
    :param subject: 邮件主题
    :param content: 邮件内容
    :return: 答案
    """
    rs = send_email_tool(to_email, subject, content)
    return rs

@mcp.tool(name="faiss_tool",description="RAG工具,执行RAG问答")
def rag_tool(query: str) -> str:
    """
    faiss工具,执行RAG问答
    :param query: 问题
    :return: 答案
    """
    rs = faiss_tool(query)
    return rs

@mcp.tool(name="amap_tool",description="高德地图工具,执行医院位置查询")
def map_tool(center: str, determination: str) -> list:
    """
    高德地图工具,执行医院位置查询
    :param center: 起点城市
    :param determination: 目标医院类型名称
    :return: 答案
    """
    res_list = amap_service_tool(center, determination)
    return res_list

@mcp.tool(name="generate_word_tool", description="生成 Word 医疗报告文档")
def generate_word_tool(content: str, title: str = "医疗报告",doc_type: str = "word") -> str:
    """
    根据输入内容生成 Word 医疗报告文档
    :param content: 报告内容
    :param title: 文档标题
    :return: 生成的 Word 文件路径
    """
    if doc_type == "word":
        return generate_word(content, title)
    elif doc_type == "pdf":
        return generate_pdf(content, title)
    else:
        return f"未知的文档类型: {doc_type}"

if __name__ == '__main__':
    # 启动MCP服务器
    print("正在启动 MCP 服务器...")
    mcp.run(
        host="0.0.0.0", # 监听所有ip
        port=8008,
        transport="sse" # sse传输方式
    )