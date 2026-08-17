import asyncio
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters, ClientSession

async def test():
    file = "D:\\Programming\\AI250601\\FastMCP_test\\mcp_service\\server_stdio.py"
    # 构建一个命令
    params = StdioServerParameters(args=[file], command="python")
    # 采用异步调用服务器
    async with stdio_client(params) as (read, write):
        # 创建 ClientSession
        async with ClientSession(read, write) as session:
            # 初始化
            print("初始化服务器")
            await session.initialize()
            print("测试mcp服务器调用")
            rs = await session.list_tools()
            print(rs)
            print("=====测试工具调用=====")
            rs1 = await session.call_tool(
                "hello_tool", {"name": "张三"}
            )
            rs2 = await session.call_tool(
                "count_tool",
                arguments={"a": 1, "b": 2}
            )
            print(rs1.structuredContent["result"],rs2.structuredContent["result"])

if __name__ == '__main__':
    asyncio.run(test())