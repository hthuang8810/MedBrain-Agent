import vosk
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

class MyModel:
    _llm = None
    _embedding = None
    _vosk_model = None   # 保存 vosk.Model 实例
    _vosk_path = os.getenv("VOSK_MODEL")

    def __init__(self):
        self.model_name = os.getenv("MODEL_NAME")
        self._embedding_name = os.getenv("EMBEDDING_MODEL")

    def get_line_model(self):
        if self._llm is None:
            self._llm = ChatOpenAI(model=self.model_name)
        return self._llm

    def get_embedding_model(self):
        if self._embedding is None:
            self._embedding = HuggingFaceEmbeddings(model_name=self._embedding_name)
        return self._embedding

    @classmethod
    def get_vosk_model(cls):
        """
        返回 vosk.Model 实例（全局加载一次）
        不再返回 KaldiRecognizer（那是临时对象）
        """
        if cls._vosk_model is None:
            print(" 正在加载 VOSK 模型，请稍候...")
            cls._vosk_model = vosk.Model(cls._vosk_path)
            print(" VOSK 模型加载完成:", cls._vosk_path)
        return cls._vosk_model


if __name__ == '__main__':
    model = MyModel()
    llm = model.get_line_model()
    print(llm.invoke("hello world"))
