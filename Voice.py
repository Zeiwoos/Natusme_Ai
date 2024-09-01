import os
import requests
from PyQt5.QtGui import QIcon, QImage, QPixmap, QCursor
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl
from PyQt5.QtWidgets import (
    QWidget, QLabel, QAction, QMenu, QSystemTrayIcon,
    QDesktopWidget, QHBoxLayout, QVBoxLayout, QPushButton, QApplication, QLineEdit
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


def playSound(path):
    player = QMediaPlayer()
    if os.path.exists(path):
        url = QUrl.fromLocalFile(path)
        content = QMediaContent(url)
        player.setMedia(content)
        player.play()
    else:
        print(f"Sound file not found: {path}")


def getVoice(user_input):
    # 提示用户输入text值

    # 定义API请求的URL和数据
    url = "http://127.0.0.1:9880"
    data = {
        "refer_wav_path": "お前のことだから、少しかっこいいなーとか思って言ったのだろう。んで、引くに引けない状態になったんだろ.wav",
        "prompt_text": "お前のことだから、少しかっこいいなーとか思って言ったのだろう。んで、引くに引けない状態になったんだろ",
        "prompt_language": "ja",
        "text": user_input,
        "text_language": "ja"
    }

    # 发送POST请求到指定URL
    response = requests.post(url, json=data)

    # 检查响应状态码
    if response.status_code == 400:
        raise Exception(f"请求错误{response.message}")

    # 将返回的内容保存为WAV文件
    with open("success.wav", "wb") as f:
        f.write(response.content)

    return "success.wav"

def main():
    # 提示用户输入text值
    user_input = input("请输入要合成的文本 (日文): ")
    getVoice(user_input)
    playSound("success.wav")

if __name__ == "__main__":
    main()

