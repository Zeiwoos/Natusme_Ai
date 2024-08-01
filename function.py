# function.py

import os
import random
import mysql.connector
from PyQt5.QtGui import QImage, QGuiApplication

def loadImage(imagepath: str) -> QImage:
    image = QImage()
    if not image.load(imagepath):
        raise FileNotFoundError(f"Image file not found: {imagepath}")
    return image

def randomPosition(widget):
    screen_geo = QGuiApplication.primaryScreen().geometry()
    pet_geo = widget.geometry()
    width = (screen_geo.width() - pet_geo.width()) * random.random()
    height = (screen_geo.height() - pet_geo.height()) * random.random()
    widget.move(int(width), int(height))

def connect_to_db():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # 确保使用正确的用户名
        password='password',  # 确保使用正确的密码
        database='natusme'
    )
    return connection
