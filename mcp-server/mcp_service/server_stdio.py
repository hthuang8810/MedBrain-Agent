from fastmcp import FastMCP
from mcp_service.count_service.count_tool import count_add
from mcp_service.hello_service.hello_tool import hello_tool
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 1.定义mcp应用程序
mcp = FastMCP(
    name="mcp服务",
    version="0.1.0",
)
# 2.定义mcp工具
@mcp.tool(name="hello_tool",description="你好的问候工具")
def hello(name: str) -> str:
    """
    问候工具
    :param name: 姓名
    :return: 返回字符串
    """
    rs = hello_tool(name)
    return rs


@mcp.tool(name="count_tool",description="加法工具")
def count(a: int, b: int) -> int:
    """
    两个数相加
    :param a: 第一个数
    :param b: 第二个数
    :return: 和
    """
    rs = count_add(a, b)
    return rs


if __name__ == '__main__':
    mcp.run(
        transport="stdio" # sse传输方式
    )