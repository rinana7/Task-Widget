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

        self.label = QLabel(self)
        self.frames = [QPixmap("cat_frame.png"), QPixmap("cat_frame2.png")]
        self.frame_index = 0

        self.x = 100
        self.y = 800

        self.timer = QTimer()
        self.timer.timeout.connect(self.walk)
        self.timer.start(150)
        self.show()
    def walk(self):
        self.label.setPixmap(self.frames[self.frame_index])
        self.frame_index = (self.frame_index+1)%len(self.frames)
        self.x+=5
        self.move(self.x, self.y)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = TaskWidget()
    sys.exit(app.exec())