import asyncio
from fastmcp import Client
from pydantic import BaseModel, Field # 输入参数验证
from dotenv import load_dotenv
from langchain.tools import tool

# 加载环境变量
load_dotenv()

class AmapToolArgs(BaseModel):
    # 输入参数
    center: str = Field(..., description="起点城市")
    determination: str = Field(..., description="目标医院名称")

@tool(args_schema=AmapToolArgs)
def amap_tool(center: str, determination: str)->list:
    """
    高德地图工具,执行医院位置查询
    :param center: 起点城市
    :param determination: 目标医院类型名称
    :return: 答案
    """
    try:
        async def run_amap_tool():
            async with Client("http://localhost:8008/sse") as client:
                res_list = await client.call_tool("amap_tool", {"center":center,"determination":determination})
                return  res_list
        return asyncio.run(run_amap_tool())
    except Exception as e:
        print("执行异常：",e)
        return "高德地图查询失败"

