import os
import random
import sys
import webbrowser
from PyQt5.QtGui import QIcon, QImage, QPixmap, QCursor
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QAction, QMenu,
    QSystemTrayIcon, QDesktopWidget, QMessageBox
)
import config as cfg


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
        self.resize(512, 512)
        self.randomPosition()
        self.show()

        self.is_running_action = False
        self.action_images = []
        self.action_pointer = 0
        self.action_max_len = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.randomAct)
        self.timer.start(200)

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
        self.image.setPixmap(QPixmap.fromImage(image))

    def preloadPetImages(self):
        pet_name = random.choice(list(cfg.PET_ACTIONS_MAP.keys()))
        actions = cfg.PET_ACTIONS_MAP[pet_name]
        pet_images = []
        for action in actions:
            pet_images.append(
                [self.loadImage(os.path.join(cfg.ROOT_DIR, pet_name, '0-' + item + '.png')) for item in action]
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

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def loadImage(self, imagepath: str) -> QImage:
        image = QImage()
        image.load(imagepath)
        return image

    def randomPosition(self):
        screen_geo = QDesktopWidget().screenGeometry()
        pet_geo = self.geometry()
        width = (screen_geo.width() - pet_geo.width()) * random.random()
        height = (screen_geo.height() - pet_geo.height()) * random.random()
        self.move(int(width), int(height))

    def showDialog(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("桌面宠物")
        msg.setText("早上好")
        msg.setInformativeText("今天想做什么？")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def quit(self):
        self.close()
        QApplication.quit()

