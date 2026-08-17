from vosk import Model, KaldiRecognizer
import pyaudio
import json
from dotenv import load_dotenv
import os
import time
def vosk_speech_to_text():
    load_dotenv()
    # 加载模型（替换为你的模型路径）# 中文模型
    model_path = os.getenv("VOSK_MODEL")
    print("模型路径:",model_path)
    # 创建模型实例
    model = Model(model_path)
    # 创建识别器实例
    recognizer = KaldiRecognizer(model, 16000)
    # 创建PyAudio实例
    p = pyaudio.PyAudio()
    # 创建音频流
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=4096)

    print("请说话...")
    # 开始录音
    stream.start_stream()
    try:
        while True:
            # 读取音频数据
            data = stream.read(4096)
            # 将音频数据传递给识别器
            if recognizer.AcceptWaveform(data):
                # 获取识别结果
                result = json.loads(recognizer.Result())
                if result['text']:
                    print(f"识别结果: {result['text']}")
                    return result['text']
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("停止录音")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


# 使用
if __name__ == '__main__':

    text = vosk_speech_to_text()
    print(text)