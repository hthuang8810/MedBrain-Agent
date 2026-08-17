from pydantic import BaseModel,Field
from langchain.tools import tool
from fastmcp import Client
import asyncio

# 工具参数的验证
class EmailToolArgs(BaseModel):
    # 收件人邮箱， Field (...，description 描述 -> 智能体需要根据描述进行参数填写)
    to_email: str = Field(..., description="收件人邮箱")
    # 邮件主题， Field()同上
    subject: str = Field(..., description="邮件主题")
    # 邮件内容， Field()同上
    content: str = Field(..., description="邮件内容")

@tool(args_schema=EmailToolArgs)
def send_email_tool(to_email:str, subject:str, content:str)->str:
    """
    发送邮件
    """
    try:
        async def run_email_tool():
            async with Client("http://localhost:8008/sse") as client:
                rs = await client.call_tool("send_email_tool", {"to_email": to_email, "subject": subject, "content": content})
                return  rs
        return asyncio.run(run_email_tool())
    except Exception as e:
        print("发送异常：",e)
        return "发送失败"