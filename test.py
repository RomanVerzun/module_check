from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import *

import sys

app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()
engine.load('window.qml')

sys.exit(app.exec())