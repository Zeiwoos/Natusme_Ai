import os
import mysql.connector
import random
import subprocess
from PyQt5.QtGui import QIcon, QImage, QPixmap, QCursor
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl
from PyQt5.QtWidgets import (
    QWidget, QLabel, QAction, QMenu,
    QSystemTrayIcon, QDesktopWidget, QHBoxLayout, QVBoxLayout, QPushButton, QApplication, QLineEdit
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import config as cfg
from function import loadImage, randomPosition, connect_to_db
from dialog import CustomDialog


class DesktopPet(QWidget):
    def __init__(self, parent=None, **kwargs):
        super(DesktopPet, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()
        self.pet_images, iconpath = self.preloadPetImages()

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

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Add pet image label
        layout.addWidget(self.image)

        # Add function buttons
        self.button_layout = QHBoxLayout()

        # 登录输入框
        self.login_layout = QVBoxLayout()

        self.input_message = QLineEdit(self)
        self.input_message.setPlaceholderText('请输入对话内容')
        self.input_message.setFixedSize(150, 30)
        self.input_message.hide()
        self.login_layout.addWidget(self.input_message)

        self.input_password = QLineEdit(self)
        self.input_password.setPlaceholderText('请输入密码')
        self.input_password.setFixedSize(150, 30)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.hide()
        self.login_layout.addWidget(self.input_password)

        self.button_talk = QPushButton('对话', self)
        self.button_talk.clicked.connect(self.showDialogInput)
        self.button_talk.setFixedSize(50, 30)
        self.button_layout.addWidget(self.button_talk)

        self.button_login = QPushButton('登录', self)
        self.button_login.clicked.connect(self.showLoginDialog)
        self.button_login.setFixedSize(50, 30)
        self.button_layout.addWidget(self.button_login)

        self.button_sign_in = QPushButton('签到', self)
        self.button_sign_in.clicked.connect(self.signIn)
        self.button_sign_in.setFixedSize(50, 30)
        self.button_layout.addWidget(self.button_sign_in)

        layout.addLayout(self.button_layout)
        layout.addLayout(self.login_layout)
        self.setLayout(layout)

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

    def showContextMenu(self, pos):
        self.tray_icon.contextMenu().exec_(pos)

    def showDialogInput(self):
        self.button_talk.hide()
        self.button_login.hide()
        self.button_sign_in.hide()
        self.input_message.setPlaceholderText('请输入对话内容')
        self.safeDisconnect(self.input_message.returnPressed)  # 确保不连接到登录功能
        self.input_message.returnPressed.connect(self.submitMessage)  # 连接到对话功能
        self.input_message.show()
        self.input_message.setFocus()

    def submitMessage(self):
        message = self.input_message.text()
        self.dialog.showDialog(message, timeout=3000)
        self.dialog.move(self.x(), self.y() - self.dialog.height() - 10)
        self.input_message.hide()
        self.input_message.clear()
        self.button_talk.show()
        self.button_login.show()
        self.button_sign_in.show()

    def showLoginDialog(self):
        self.input_message.setPlaceholderText('请输入用户名')
        self.input_password.setPlaceholderText('请输入密码')
        self.input_password.setEchoMode(QLineEdit.Password)
        self.button_talk.hide()
        self.button_login.hide()
        self.button_sign_in.hide()
        self.input_message.show()
        self.input_password.show()
        self.input_message.setFocus()

        # 处理回车键事件，确保焦点移动到密码框
        self.safeDisconnect(self.input_message.returnPressed)
        self.input_message.returnPressed.connect(self.focusOnPassword)
        self.input_password.returnPressed.connect(self.login)

    def focusOnPassword(self):
        self.input_password.setFocus()

    def login(self):
        username = self.input_message.text()
        password = self.input_password.text()

        print(f"Username: {username}, Password: {password}")

        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            if user:
                print("Login successful.")
            else:
                print("Login failed.")
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Connect Error: {err}")
        self.input_message.hide()
        self.input_message.clear()
        self.input_password.hide()
        self.input_password.clear()
        self.button_talk.show()
        self.button_login.show()
        self.button_sign_in.show()
        self.safeDisconnect(self.input_password.returnPressed)

    def signIn(self):
        print("Sign-in function is called.")
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
