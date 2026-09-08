import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
import requests

class TaskWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint 
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(self)

        raw_frame1 = QPixmap("assets/cat-frame.png")
        raw_frame2 = QPixmap("assets/cat-frame2.png")

        frame1 = raw_frame1.scaledToWidth(64, Qt.TransformationMode.SmoothTransformation)
        frame2 = raw_frame2.scaledToWidth(57, Qt.TransformationMode.SmoothTransformation)

        if frame1.isNull():
            print("Warning: cat_frame1.png not found or failed to load!")
            self.frames = []
        else:
            self.frames = [frame1,frame1, frame2, frame2]

        self.frame_index = 0

        self.x = 200
        self.y = 200
        self.move(self.x, self.y)

        self.timer = QTimer()
        self.timer.timeout.connect(self.walk)
        self.timer.start(150)
        self.show()


    def walk(self):
        if self.frames:
            self.label.setPixmap(self.frames[self.frame_index])
            self.frame_index = (self.frame_index+1)%len(self.frames)

        self.label.adjustSize()
        self.adjustSize()
        self.x+=3
        self.move(self.x, self.y)

    LAT="21.3069"
    LON="157.8583"
    def get_weather(lat=LAT, lon=LON):
        headers = {
            "User-Agent": "(TaskWidgetApp, taskwidget@example.com)"
        }
        try:
            point_url = f"https://api.weather.gov/points/{lat},{lon}"
            point_res = requests.get(point_url, headers=headers, timeout=5).json()
            forecast_url = point_res["properties"]["forecast"]
            forecast_res = requests.get(forecast_url, headers=headers, timeout=5).json
            current_period = forecast_res["properties"]["periods"][0]

            temp = current_period["temperature"]
            unit = current_period["tempertureUnit"]
            desc = current_period["shortForecast"]
            return f"It's {temp}°{unit} & {desc}"
        except Exception as e:
            return "No connection"

    def update_weather(self):
        msg = get_weather(LAT,LON)
        self.bubble.setText(f"🐱: {msg}")
        self.adjustSize()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = TaskWidget()
    sys.exit(app.exec())