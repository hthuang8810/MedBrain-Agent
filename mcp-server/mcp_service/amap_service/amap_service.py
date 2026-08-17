import requests
import os
from pydantic import BaseModel, Field  # 输入参数验证
from dotenv import load_dotenv
from langchain.tools import tool

# 加载环境变量
load_dotenv()


class AmapToolArgs(BaseModel):
    # 输入参数
    center: str = Field(..., description="起点城市")
    determination: str = Field(..., description="医院类型名称")


def amap_service_tool(center: str, determination: str) -> list:
    """
    医院地址推荐
    """
    try:
        # 创建请求地址
        url = f"https://restapi.amap.com/v5/place/text"
        params = {
            "key": os.getenv("AMAP_KEY"),
            "keywords": determination,
            # "types": "050000",
            "city": center,
            "output": "JSON",  # 输出数据
        }
        res = requests.get(url, params=params)
        data = res.json()
        res_lst = []
        for poi in data["pois"]:
            info = f'{poi["name"]}----{poi["type"]}\n{poi["cityname"]}{poi["adname"]}{poi["address"]}'
            res_lst.append(info)
        return res_lst

    except Exception as e:
        print("执行异常：", e)
        return "高德地图查询失败"

if __name__ == '__main__':
    print(amap_service_tool("成都", "肿瘤医院"))

