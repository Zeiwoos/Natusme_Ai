import sys
from PyQt5.QtWidgets import QApplication
from function import DesktopPet

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec_())
