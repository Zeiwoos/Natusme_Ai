from PyQt5.QtGui import QFont, QClipboard
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QApplication


class CustomDialog(QWidget):
    def __init__(self, parent=None):
        super(CustomDialog, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.text = self.gettext()

        layout = QVBoxLayout()

        # 创建显示消息的标签
        self.label = QLabel(self.text, self)
        self.label.setFont(QFont('Arial', 12))
        self.label.setStyleSheet("color: pink; background-color: gray; border: 2px solid pink; padding: 10px;")
        self.label.setWordWrap(True)  # 允许文字换行
        layout.addWidget(self.label)

        # 限制对话框最大宽度
        self.setFixedWidth(300)

        # 创建复制按钮
        self.copy_button = QPushButton("复制", self)
        self.copy_button.setStyleSheet("background-color: lightblue; color: black;")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(self.copy_button)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide)

    def showDialog(self, message, timeout):
        self.label.setText(message)
        self.adjustSize()  # 根据内容自动调整窗口大小
        self.show()
        self.timer.start(timeout)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.label.text())

    def gettext(self):
        return ""
