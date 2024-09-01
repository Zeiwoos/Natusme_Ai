import os
import mysql.connector
import random
import subprocess
import json
import requests
from PyQt5.QtGui import QIcon, QImage, QPixmap, QCursor
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl
from PyQt5.QtWidgets import (
    QWidget, QLabel, QAction, QMenu, QSystemTrayIcon,
    QDesktopWidget, QHBoxLayout, QVBoxLayout, QPushButton, QApplication, QLineEdit
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

import chatgpt
import config as cfg
from function import loadImage, randomPosition, connect_to_db
from dialog import CustomDialog
import weather
# from SoVITS import api2
import Voice
import translate

class SettingsWindow(QWidget):
    def __init__(self, desktop_pet):
        super(SettingsWindow, self).__init__()
        self.desktop_pet = desktop_pet  # 引用DesktopPet实例
        self.initUI()

    def initUI(self):
        self.setWindowTitle("设置")
        self.setGeometry(300, 300, 300, 200)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.updateUI()

    def updateUI(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        if self.desktop_pet.is_logged_in:
            self.showLoggedInOptions()
        else:
            self.showLoggedOutOptions()

    def showLoggedOutOptions(self):
        self.button_register = QPushButton('注册', self)
        self.button_register.setFixedSize(100, 30)
        self.button_register.setStyleSheet("background-color: #00FFFF; color: black;")
        self.button_register.clicked.connect(self.desktop_pet.showRegisterDialog)
        self.layout.addWidget(self.button_register)

        self.button_login = QPushButton('登录', self)
        self.button_login.setFixedSize(100, 30)
        self.button_login.setStyleSheet("background-color: #00FFFF; color: black;")
        self.button_login.clicked.connect(self.desktop_pet.showLoginDialog)
        self.layout.addWidget(self.button_login)

    def showLoggedInOptions(self):
        self.button_sign_in = QPushButton('签到', self)
        self.button_sign_in.setFixedSize(100, 30)
        self.button_sign_in.setStyleSheet("background-color: #00FFFF; color: black;")
        self.button_sign_in.clicked.connect(self.desktop_pet.signIn)
        self.layout.addWidget(self.button_sign_in)

        self.button_weather = QPushButton('查询天气', self)
        self.button_weather.setFixedSize(100, 30)
        self.button_weather.setStyleSheet("background-color: #00FFFF; color: black;")
        self.button_weather.clicked.connect(self.desktop_pet.queryWeather)
        self.layout.addWidget(self.button_weather)

        self.button_logout = QPushButton('登出', self)
        self.button_logout.setFixedSize(100, 30)
        self.button_logout.setStyleSheet("background-color: pink; color: red;")
        self.button_logout.clicked.connect(self.desktop_pet.logout)
        self.layout.addWidget(self.button_logout)

    def closeEvent(self, event):
        self.hide()
        event.ignore()

class DesktopPet(QWidget):
    def __init__(self, parent=None, **kwargs):
        super(DesktopPet, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()
        self.pet_images, iconpath = self.preloadPetImages()

        self.is_logged_in = False  # 用于跟踪用户是否已登录
        self.load_login_status()  # 尝试加载本地的登录状态

        quit_action = QAction('退出', self, triggered=self.quit)
        quit_action.setIcon(QIcon(iconpath))
        self.tray_icon_menu = QMenu(self)
        self.tray_icon_menu.addAction(quit_action)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(iconpath))
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        self.tray_icon.show()

        self.image = QLabel(self)
        self.setImage(self.pet_images[0][0])

        self.is_follow_mouse = False
        self.mouse_drag_pos = QPoint()
        self.resize(256, 256)
        randomPosition(self)
        self.show()

        self.is_running_action = False
        self.action_images = []
        self.action_pointer = 0
        self.action_max_len = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.randomAct)
        self.timer.start(500)

        self.player = QMediaPlayer()
        self.dialog = CustomDialog()
        self.settings_window = None  # 设置窗口引用

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.image)

        self.input_message = QLineEdit(self)
        self.input_message.setFixedSize(150, 30)
        self.input_message.hide()

        self.input_password = QLineEdit(self)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setFixedSize(150, 30)
        self.input_password.hide()

        self.layout.addWidget(self.input_message)
        self.layout.addWidget(self.input_password)

        self.button_talk = QPushButton('对话', self)
        self.button_talk.clicked.connect(self.showDialogInput)
        self.button_talk.setFixedSize(80, 30)
        self.button_talk.setStyleSheet("background-color: #00FFFF; color: black;")
        self.button_talk.hide()

        self.button_settings = QPushButton('设置', self)
        self.button_settings.clicked.connect(self.openSettings)
        self.button_settings.setFixedSize(80, 30)
        self.button_settings.setStyleSheet("background-color: #00FFFF; color: black;")

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.button_talk)
        button_layout.addWidget(self.button_settings)
        button_layout.addStretch(1)

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

        if self.is_logged_in:
            self.showLoggedInButtons()
        else:
            self.showLoggedOutButtons()

    def showLoggedOutButtons(self):
        self.button_talk.hide()
        self.button_settings.show()

    def showLoggedInButtons(self):
        self.button_talk.show()
        self.button_settings.show()

    def openSettings(self):
        if not self.settings_window:
            self.settings_window = SettingsWindow(self)
        self.settings_window.updateUI()
        self.settings_window.show()

    def randomAct(self):
        if not self.is_running_action:
            self.is_running_action = True
            self.action_images = random.choice(self.pet_images)
            self.action_max_len = len(self.action_images)
            self.action_pointer = 0
        self.runFrame()

    def runFrame(self):
        if self.action_pointer < self.action_max_len:
            self.setImage(self.action_images[self.action_pointer])
            self.action_pointer += 1
        else:
            self.is_running_action = False
            self.action_pointer = 0
            self.action_max_len = 0

    def setImage(self, image: QImage):
        pixmap = QPixmap.fromImage(image).scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image.setPixmap(pixmap)

    def preloadPetImages(self):
        pet_name = random.choice(list(cfg.PET_ACTIONS_MAP.keys()))
        actions = cfg.PET_ACTIONS_MAP[pet_name]
        pet_images = []
        for action in actions:
            pet_images.append(
                [loadImage(os.path.join(cfg.ROOT_DIR, pet_name, '0-' + item + '.png')) for item in action]
            )
        iconpath = os.path.join(cfg.ROOT_DIR, pet_name, '0-1.png')
        return pet_images, iconpath

    def mousePressEvent(self, event):
        hello_voice_path = "resources/voice/Ciallo/こんにちは、私の名前は夏目藍です.wav"
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
        elif event.button() == Qt.RightButton:
            self.showDialog()
            self.playSound(hello_voice_path)

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()
            # 调整对话框位置到桌宠左上方
            self.dialog.move(self.x() - self.dialog.width(), self.y() - self.dialog.height())

    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def showDialog(self):
        # 设置对话框在桌宠左上方（右侧对齐桌宠左侧）
        self.dialog.move(self.x() - self.dialog.width(), self.y() - self.dialog.height())
        self.dialog.showDialog("你好，今天要做些什么？", timeout=30000)  # 持续时间 30 秒

    def showDialogInput(self):
        self.input_message.setPlaceholderText('请输入对话内容')
        self.safeDisconnect(self.input_message.returnPressed)
        self.input_message.returnPressed.connect(self.fetchResponce)
        self.input_message.show()
        self.input_message.setFocus()

    def submitMessage(self):
        message = self.input_message.text()
        self.dialog.showDialog(message, timeout=30000)  # 持续时间 30 秒
        self.dialog.move(self.x() - self.dialog.width(), self.y() - self.dialog.height())  # 对话框位置调整
        self.input_message.hide()
        self.input_message.clear()

    def showRegisterDialog(self):
        self.settings_window.hide()
        self.input_message.setPlaceholderText('请输入注册用户名')
        self.input_password.setPlaceholderText('请输入注册密码')
        self.input_message.show()
        self.input_password.show()
        self.input_message.setFocus()

        self.safeDisconnect(self.input_message.returnPressed)
        self.input_message.returnPressed.connect(self.focusOnPassword)
        self.input_password.returnPressed.connect(self.register)

    def register(self):
        username = self.input_message.text()
        password = self.input_password.text()

        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                print("用户名已存在。")
                self.dialog.showDialog("用户名已存在，请重试。", timeout=30000)
                self.input_message.clear()
                self.input_password.clear()
                self.showRegisterDialog()
            else:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
                print("注册成功。")
                self.dialog.showDialog("注册成功，请登录。", timeout=30000)
                self.clearInputFields()
                self.showLoginDialog()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"连接错误: {err}")
            self.dialog.showDialog(f"连接错误: {err}", timeout=30000)

    def showLoginDialog(self):
        self.settings_window.hide()
        self.input_message.setPlaceholderText('请输入用户名')
        self.input_password.setPlaceholderText('请输入密码')
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_message.show()
        self.input_password.show()
        self.input_message.setFocus()

        self.safeDisconnect(self.input_message.returnPressed)
        self.input_message.returnPressed.connect(self.focusOnPassword)
        self.input_password.returnPressed.connect(self.login)

    def focusOnPassword(self):
        self.input_password.setFocus()

    def login(self):
        username = self.input_message.text()
        password = self.input_password.text()

        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            if user:
                print("登录成功。")
                self.is_logged_in = True  # 标记用户已登录
                self.save_login_status(username)  # 保存登录状态
                self.dialog.showDialog("登录成功！", timeout=30000)
                self.showLoggedInButtons()
                self.openSettings()
            else:
                print("登录失败。")
                self.dialog.showDialog("登录失败，请重试。", timeout=30000)
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"连接错误: {err}")
            self.dialog.showDialog(f"连接错误: {err}", timeout=30000)

        self.clearInputFields()

    def logout(self):
        self.is_logged_in = False
        self.clear_login_status()
        self.dialog.showDialog("已退出登录。", timeout=30000)
        if self.settings_window:
            self.settings_window.hide()
        self.showLoggedOutButtons()

    def clearInputFields(self):
        self.input_message.hide()
        self.input_message.clear()
        self.input_password.hide()
        self.input_password.clear()

    def signIn(self):
        self.settings_window.hide()
        print("签到功能已调用。")
        os.system('start cmd.exe /K sign_in.bat')

    def queryWeather(self):
        # 显示输入框让用户输入城市名称
        self.input_message.setPlaceholderText('请输入城市名')
        try:
            self.input_message.returnPressed.disconnect()  # 尝试断开所有连接
        except TypeError:
            pass  # 如果没有连接，不进行任何处理
        self.input_message.returnPressed.connect(self.fetchWeather)  # 连接到查询天气的函数
        self.input_message.show()
        self.input_message.setFocus()

    def fetchWeather(self):
        try:
            city = self.input_message.text()
            if not city:
                raise ValueError("城市名不能为空")
            # print("天气已查询")
            weather_info = weather.get_weather(city)
            self.dialog.showDialog(weather_info, timeout=5000)
            processed_weather_info = translate.Start(weather_info, "jp")
            print(processed_weather_info)
            weather_voice_path = Voice.getVoice(processed_weather_info)
            self.playSound(weather_voice_path)
        except Exception as e:
            error_message = f"查询天气时发生错误: {str(e)}"
            self.dialog.showDialog(error_message, timeout=5000)
        finally:
            self.clearInputFields()  # 查询完后清除输入框并恢复按钮


    def fetchResponce(self):
        try:
            message = self.input_message.text()
            if not message:
                raise ValueError("输入内容不能为空")

            response_info = chatgpt.get_response(message)

            formatted_response = '\n'.join(response_info[i:i + 15] for i in range(0, len(response_info), 15))

            self.dialog.showDialog(formatted_response, timeout=30000)  # 持续时间 30 秒

        except Exception as e:
            error_message = f"未知错误发生: {str(e)}"
            self.dialog.showDialog(error_message, timeout=30000)
        finally:
            self.clearInputFields()

    def quit(self):
        self.close()
        QApplication.quit()

    def playSound(self,path):
        sound_path = os.path.join(path)
        if os.path.exists(sound_path):
            url = QUrl.fromLocalFile(sound_path)
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.play()
        else:
            print(f"Sound file not found: {sound_path}")

    def safeDisconnect(self, signal):
        try:
            signal.disconnect()
        except TypeError:
            pass

    def save_login_status(self, username):
        with open("login_status.json", "w") as f:
            json.dump({"username": username}, f)

    def load_login_status(self):
        if os.path.exists("login_status.json"):
            with open("login_status.json", "r") as f:
                data = json.load(f)
                if "username" in data:
                    self.is_logged_in = True

    def clear_login_status(self):
        if os.path.exists("login_status.json"):
            os.remove("login_status.json")


