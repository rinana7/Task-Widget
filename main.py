import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
import requests
import ctypes

LAT="21.3069"
LON="-157.8583"
def get_weather(lat=LAT, lon=LON):
    headers = {
        "User-Agent": "(TaskWidgetApp, taskwidget@example.com)"
    }
    try:
        point_url = f"https://api.weather.gov/points/{lat},{lon}"
        point_res = requests.get(point_url, headers=headers, timeout=5).json()
        forecast_url = point_res["properties"]["forecast"]

        forecast_res = requests.get(forecast_url, headers=headers, timeout=5).json()
        current = forecast_res["properties"]["periods"][0]

        return f"{current['temperature']}°{current['temperatureUnit']} • {current['shortForecast']}"   
    except Exception as e:
        print("Weather Error:", e)
        return "No connection"

    
class TaskWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        self.bubble = QLabel("Loading...", self)
        self.bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bubble.setStyleSheet("""
            QLabel {
                background-color: #2D3748;
                color: #EDF2F7;
                border: 2px solid #4A5568;
                border-radius: 10px;
                padding: 6px 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.bubble, alignment=Qt.AlignmentFlag.AlignCenter)

        self.cat_label = QLabel(self)
        layout.addWidget(self.cat_label, alignment=Qt.AlignmentFlag.AlignCenter)

        raw_frame1 = QPixmap("assets/cat-frame.png")
        raw_frame2 = QPixmap("assets/cat-frame2.png")

        if raw_frame1.isNull() or raw_frame2.isNull():
            print("Error: Could not load cat assets")
        frame1 = raw_frame1.scaledToWidth(64, Qt.TransformationMode.FastTransformation)
        frame2 = raw_frame2.scaledToWidth(57, Qt.TransformationMode.FastTransformation)

        self.frames = [frame1,frame1, frame2, frame2]

        self.frame_index = 0
        if self.frames:
            self.cat_label.setPixmap(self.frames[0])

        self.x = 200
        self.y = 200
        self.move(self.x, self.y)

        self.timer = QTimer()
        self.timer.timeout.connect(self.walk)
        self.timer.start(150)

        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(900000)

        self.show()
        self.update_weather()


    def walk(self):
        if self.frames:
            self.cat_label.setPixmap(self.frames[self.frame_index])
            self.frame_index = (self.frame_index+1)%len(self.frames)

        self.cat_label.adjustSize()
        self.adjustSize()
        self.x+=3
        if self.x > 1400:
            self.x = -60
        self.move(self.x, self.y)

    def update_weather(self):
        msg = get_weather(LAT,LON)
        self.bubble.setText(f"🐱: {msg}")
        self.adjustSize()

    def showEvent(self, event):
        super().showEvent(event)
        try:
            import objc
            NSWindowCollectionBehaviorCanJoinAllSpaces = 1 << 0
            NSWindowCollectionBehaviorStationary = 1 << 4
            
            ns_view = objc.objc_object(c_void_p=ctypes.c_void_p(int(self.winId())))
            ns_window = ns_view.window()
            
            if ns_window:
                behavior = NSWindowCollectionBehaviorCanJoinAllSpaces | NSWindowCollectionBehaviorStationary
                ns_window.setCollectionBehavior_(behavior)
                ns_window.setLevel_(3) 
        except Exception as e:
            print("Space Behavior Error:", e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = TaskWidget()
    sys.exit(app.exec())