import asyncio
from fastmcp import Client

# 定义一个异步函数
async def test():
    # 调用mcp服务端
    async with Client("http://localhost:8008/sse") as sse:
        print("测试MCP服务调用")
        print("查看一下当前的服务的所有工具")
        tools = await sse.list_tools()
        for tool in tools:
            print(f"工具名称{tool.name}")
            print(f"工具描述{tool.description}")
            print(tool.inputSchema)
            print(tool.outputSchema)
        print("=====测试工具调用=====")
        rs1 = await sse.call_tool(
            "hello_tool",{"name": "张三"}
        )
        rs2 = await sse.call_tool(
            "count_tool",
            arguments={"a": 1,"b": 2}
        )
        rs3 = await sse.call_tool(
            "neo4j_tool",
            arguments={"query": "MATCH (d:Doctor {name: '刘洋'})-[:WORKS_AT]->(h:Hospital) RETURN h.name"}
        )
        print(rs1.data, rs2.data, rs3.data)

if __name__ == '__main__':
    asyncio.run(test())