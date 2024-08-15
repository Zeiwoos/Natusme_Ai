import os
import mysql.connector
import random
import subprocess
import json
from PyQt5.QtGui import QIcon, QImage, QPixmap, QCursor
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl
from PyQt5.QtWidgets import (
    QWidget, QLabel, QAction, QMenu, QSystemTrayIcon,
    QDesktopWidget, QHBoxLayout, QVBoxLayout, QPushButton, QApplication, QLineEdit
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import config as cfg
from function import loadImage, randomPosition, connect_to_db
from dialog import CustomDialog


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
        # 清空布局中的所有小部件
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # 根据登录状态更新界面
        if self.desktop_pet.is_logged_in:
            self.showLoggedInOptions()
        else:
            self.showLoggedOutOptions()

    def showLoggedOutOptions(self):
        self.button_register = QPushButton('注册', self)
        self.button_register.clicked.connect(self.desktop_pet.showRegisterDialog)
        self.button_register.setFixedSize(100, 30)
        self.layout.addWidget(self.button_register)

        self.button_login = QPushButton('登录', self)
        self.button_login.clicked.connect(self.desktop_pet.showLoginDialog)
        self.button_login.setFixedSize(100, 30)
        self.layout.addWidget(self.button_login)

    def showLoggedInOptions(self):
        self.button_sign_in = QPushButton('签到', self)
        self.button_sign_in.clicked.connect(self.desktop_pet.signIn)
        self.button_sign_in.setFixedSize(100, 30)
        self.layout.addWidget(self.button_sign_in)

        self.button_logout = QPushButton('登出', self)
        self.button_logout.clicked.connect(self.desktop_pet.logout)
        self.button_logout.setFixedSize(100, 30)
        self.layout.addWidget(self.button_logout)


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

        # Add pet image label
        self.layout.addWidget(self.image)

        # 初始化输入框组件
        self.input_message = QLineEdit(self)
        self.input_message.setFixedSize(150, 30)
        self.input_message.hide()  # 初始时隐藏

        self.input_password = QLineEdit(self)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setFixedSize(150, 30)
        self.input_password.hide()  # 初始时隐藏

        self.layout.addWidget(self.input_message)
        self.layout.addWidget(self.input_password)

        # 添加功能按钮
        self.button_talk = QPushButton('对话', self)
        self.button_talk.clicked.connect(self.showDialogInput)
        self.button_talk.setFixedSize(80, 30)
        self.button_talk.hide()  # 初始时隐藏

        self.button_settings = QPushButton('设置', self)
        self.button_settings.clicked.connect(self.openSettings)
        self.button_settings.setFixedSize(80, 30)

        # 设置按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # 左侧填充
        button_layout.addWidget(self.button_talk)
        button_layout.addWidget(self.button_settings)
        button_layout.addStretch(1)  # 右侧填充

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

        # 初始化时只显示设置按钮
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
        self.settings_window.updateUI()  # 根据登录状态更新设置界面
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
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
        elif event.button() == Qt.RightButton:
            self.showDialog()
            self.playSound()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()
            self.dialog.move(self.x(), self.y() - self.dialog.height() - 10)

    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def showDialog(self):
        self.dialog.showDialog("你好，今天要做些什么？", timeout=3000)
        self.dialog.move(self.x(), self.y() - self.dialog.height() - 10)

    def showDialogInput(self):
        # self.settings_window.hide()  # 隐藏设置窗口
        self.input_message.setPlaceholderText('请输入对话内容')
        self.safeDisconnect(self.input_message.returnPressed)
        self.input_message.returnPressed.connect(self.submitMessage)
        self.input_message.show()
        self.input_message.setFocus()

    def submitMessage(self):
        message = self.input_message.text()
        self.dialog.showDialog(message, timeout=3000)
        self.dialog.move(self.x(), self.y() - self.dialog.height() - 10)
        self.input_message.hide()
        self.input_message.clear()

    def showRegisterDialog(self):
        self.settings_window.hide()  # 隐藏设置窗口
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
                self.dialog.showDialog("用户名已存在，请重试。", timeout=3000)
                self.input_message.clear()
                self.input_password.clear()
                self.showRegisterDialog()  # 重新显示注册界面
            else:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
                print("注册成功。")
                self.dialog.showDialog("注册成功，请登录。", timeout=3000)
                self.clearInputFields()  # 注册成功后清空输入栏
                self.showLoginDialog()  # 注册成功后跳转到登录界面
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"连接错误: {err}")
            self.dialog.showDialog(f"连接错误: {err}", timeout=3000)

    def showLoginDialog(self):
        self.settings_window.hide()  # 隐藏设置窗口
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
                self.dialog.showDialog("登录成功！", timeout=3000)
                self.showLoggedInButtons()
                self.openSettings()  # 登录成功后打开设置窗口
            else:
                print("登录失败。")
                self.dialog.showDialog("登录失败，请重试。", timeout=3000)
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"连接错误: {err}")
            self.dialog.showDialog(f"连接错误: {err}", timeout=3000)

        self.clearInputFields()

    def logout(self):
        self.is_logged_in = False
        self.clear_login_status()
        self.dialog.showDialog("已退出登录。", timeout=3000)
        if self.settings_window:
            self.settings_window.hide()  # 退出登录时隐藏设置窗口
        self.showLoggedOutButtons()

    def clearInputFields(self):
        self.input_message.hide()
        self.input_message.clear()
        self.input_password.hide()
        self.input_password.clear()

    def signIn(self):
        self.settings_window.hide()  # 隐藏设置窗口
        print("签到功能已调用。")
        os.system('start cmd.exe /K sign_in.bat')

    def quit(self):
        self.close()
        QApplication.quit()

    def playSound(self):
        sound_path = os.path.join(cfg.ROOT_DIR, 'voice', 'Ciallo', 'こんにちは、私の名前は夏目藍です.wav')
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
            pass  # 如果信号没有连接，则忽略断开连接的操作

    def save_login_status(self, username):
        # 将登录状态保存到本地文件
        with open("login_status.json", "w") as f:
            json.dump({"username": username}, f)

    def load_login_status(self):
        # 从本地文件加载登录状态
        if os.path.exists("login_status.json"):
            with open("login_status.json", "r") as f:
                data = json.load(f)
                if "username" in data:
                    self.is_logged_in = True

    def clear_login_status(self):
        # 清除本地的登录状态文件
        if os.path.exists("login_status.json"):
            os.remove("login_status.json")
