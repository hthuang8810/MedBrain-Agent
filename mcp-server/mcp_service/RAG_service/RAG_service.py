from pydantic import BaseModel, Field # 输入参数验证
from dotenv import load_dotenv
from model.model_management import MyModel
from langchain_community.vectorstores import FAISS
import os

load_dotenv()

class FAISToolArgs(BaseModel):
    # FAISS向量数据库查询， Field (...，description 描述 -> 智能体需要根据描述进行参数填写)
    query: str = Field(..., description="FAISS向量数据库查询")

def faiss_tool(query:str)->str:
    """
    执行FAISS向量数据库查询
    """
    try:
        vs = FAISS.load_local(
            os.getenv("FAISS_PATH"),
            MyModel().get_embedding_model(),
            allow_dangerous_deserialization=True #允许使用 pickle 反序列化数据
        )
        retriever = vs.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )
        docs = retriever.invoke(query)
        return "\n".join([doc.page_content for doc in docs])

    except Exception as e:
        print("执行异常：",e)
        return "FAISS向量数据库查询失败"