import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer

class TaskWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttricute(Qt.WidgetAttribut.WA_TranslucentBackground)

        self.label = QtLabel(self)
        self.move(100, 800)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = TaskWidget()
    sys.exit(app.exec())