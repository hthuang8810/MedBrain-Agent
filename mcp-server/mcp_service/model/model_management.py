import vosk
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
import os

from sympy.integrals.risch import recognize_derivative

# 加载环境变量
load_dotenv()


# 创建一个模型管理类
class MyModel:
    # 创建一个模型变量
    _llm = None
    # 创建一个词嵌入变量
    _embedding = None
    # 创建一个语音识别变量
    _recognizer = None
    # 构造函数
    def __init__(self):
        # 获取模型名称
        self.model_name = os.getenv("MODEL_NAME")
        self._embedding_name = os.getenv("EMBEDDING_MODEL")
        self._vosk_name = os.getenv("VOSK_MODEL")

    # 加载千问模型
    def get_line_model(self):
        # 懒加载机制
        if self._llm is None:
            self._llm = ChatOpenAI(model=self.model_name)
        return self._llm

    # 加载词嵌入模型
    def get_embedding_model(self):
        if self._embedding is None:
            self._embedding = HuggingFaceEmbeddings(model_name=self._embedding_name)
        return self._embedding

    # 加载语音识别模型
    def get_vosk_model(self):
        if self._recognizer is None:
            vosk_model = vosk.Model(self._vosk_name)
            self._recognizer = vosk.KaldiRecognizer(vosk_model, 16000)
        return self._recognizer

if __name__ == '__main__':
    model = MyModel()
    llm = model.get_line_model()
    print(llm.invoke("hello world"))