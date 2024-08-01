# dialog.py

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class CustomDialog(QWidget):
    def __init__(self, parent=None):
        super(CustomDialog, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.text = self.gettext()
        layout = QVBoxLayout()
        self.label = QLabel(self.text, self)
        self.label.setFont(QFont('Arial', 12))
        self.label.setStyleSheet("color: pink; background-color: gray; border: 2px solid pink; padding: 10px;")
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.timer=QTimer(self)
        self.timer.timeout.connect(self.hide)

    def showDialog(self, message, timeout):
        self.label.setText(message)
        self.adjustSize()
        self.show()
        self.timer.start(timeout)
    def gettext(self):
        return
