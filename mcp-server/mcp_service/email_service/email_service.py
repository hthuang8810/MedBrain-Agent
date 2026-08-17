from email.mime.text import MIMEText
from pydantic import BaseModel, Field # 输入参数验证
import smtplib # 发送邮件库
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()


# 工具参数的验证
class EmailToolArgs(BaseModel):
    # 收件人邮箱， Field (...，description 描述 -> 智能体需要根据描述进行参数填写)
    to_email: str = Field(..., description="收件人邮箱")
    # 邮件主题， Field()同上
    subject: str = Field(..., description="邮件主题")
    # 邮件内容， Field()同上
    content: str = Field(..., description="邮件内容")

def send_email_tool(to_email:str, subject:str, content:str)->str:
    """
    发送邮件
    """
    try:
        # 定义邮件对象
        msg = MIMEText(content)
        # 定义发送方
        msg["From"] = os.getenv("EMAIL_USER")
        # 定义接收方
        msg["To"] = to_email
        # 定义邮件主题
        msg["Subject"] = subject
        # 链接邮件服务器
        smtp = smtplib.SMTP_SSL(os.getenv("EMAIL_HOST"), port=465)
        # 登录邮件服务器
        smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
        # 发送邮件 smtp.sendmail(发件人地址, 收件人地址, 邮件对象)
        # 邮件对象转换为字符串
        smtp.sendmail(os.getenv("EMAIL_USER"), to_email, msg.as_string())
        return "发送邮件成功"
    except Exception as e:
        print("发送异常：",e)
        return "发送失败"
