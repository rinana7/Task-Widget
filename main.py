import sys
import os
import ctypes
import requests
from PyQt6.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QMenu, QSystemTrayIcon, QPushButton
)
from PyQt6.QtGui import QPixmap, QIcon, QTransform
from PyQt6.QtCore import Qt, QTimer

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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
        self.is_paused = False
        self.is_sitting = False
        self.drag_position = None
        self.click_start_pos = None
        self.pomo_time_left = 25*60
        self.pomo_active = False

        self.pomo_timer = QTimer(self)
        self.pomo_timer.timeout.connect(self.update_pomodoro_tick)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.ToolTip
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        self.bubble = QPushButton("Loading...", self)
        self.bubble.setStyleSheet("""
            QPushButton {
                background-color: #2D3748;
                color: #EDF2F7;
                border: 2px solid #4A5568;
                border-radius: 10px;
                padding: 6px 10px;
                font-family: 'Menlo', 'Courier New', monospace;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton::menu-indicator {
                image: none;
            }
            QPushButton:hover {
                background-color: #4A5568;
            }
        """)

        self.bubble_menu = QMenu(self)
        self.bubble_menu.setStyleSheet("""
            QMenu {
                background-color: #2D3748;
                color: #EDF2F7;
                border: 1px solid #4A5568;
                font-family: 'Menlo', 'Courier New', monospace;
                font-size: 11px;
            }
            QMenu::item:selected {
                background-color: #4A5568;
            }
        """)

        pomo_menu = self.bubble_menu.addMenu("Pomodoro")
        start_pomo = pomo_menu.addAction("▶ Start Focus (25m)")
        start_pomo.triggered.connect(self.start_pomodoro)
        
        pause_pomo = pomo_menu.addAction("⏸ Pause Timer")
        pause_pomo.triggered.connect(self.pause_pomodoro)
        
        reset_pomo = pomo_menu.addAction("Reset Timer")
        reset_pomo.triggered.connect(self.reset_pomodoro)

        refresh_action = self.bubble_menu.addAction("Refresh Weather")
        refresh_action.triggered.connect(self.update_weather)
        
        self.bubble.setMenu(self.bubble_menu)
        layout.addWidget(self.bubble, alignment=Qt.AlignmentFlag.AlignCenter)

        self.cat_label = QLabel(self)
        layout.addWidget(self.cat_label, alignment=Qt.AlignmentFlag.AlignCenter)

        raw_frame1 = QPixmap(resource_path("assets/cat-frame.png"))
        raw_frame2 = QPixmap(resource_path("assets/cat-frame2.png"))

        if raw_frame1.isNull() or raw_frame2.isNull():
            print("Error: Could not load cat assets")

        frame1 = raw_frame1.scaledToWidth(64, Qt.TransformationMode.FastTransformation)
        frame2 = raw_frame2.scaledToWidth(57, Qt.TransformationMode.FastTransformation)

        self.frames = [frame1,frame1, frame2, frame2]
        self.frame_index = 0


        sit_pixmap = QPixmap(resource_path("assets/cat-sit.png"))
        
        if sit_pixmap.isNull():
            self.sit_frame = frame1
        else:
            self.sit_frame = sit_pixmap.scaledToWidth(48, Qt.TransformationMode.FastTransformation)

        if self.frames:
            self.cat_label.setPixmap(self.frames[0])

        self.x = 200
        self.y = 200
        self.dx = 3
        self.move(self.x, self.y)

        self.setup_tray_icon(raw_frame1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.walk)
        self.timer.start(150)

        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(900000)

        self.show()
        self.update_weather()

    def setup_tray_icon(self, pixmap):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(pixmap))

        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: #2D3748;
                color: #EDF2F7;
                border: 1px solid #4A5568;
                font-family: 'Menlo', 'Courier New', monospace;
                font-size: 11px;
            }
            QMenu::item:selected {
                background-color: #4A5568;
            }
        """)
        toggle_action = tray_menu.addAction("Show/Hide Cat")
        toggle_action.triggered.connect(self.toggle_visibility)

        quit_action = tray_menu.addAction("Exit App")
        quit_action.triggered.connect(QApplication.quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def toggle_sit(self):
        self.is_sitting = not self.is_sitting
        if self.is_sitting:
            pixmap = self.sit_frame
            if self.dx < 0:
                pixmap = pixmap.transformed(QTransform().scale(-1, 1))
            self.cat_label.setPixmap(pixmap)
            self.cat_label.adjustSize()
            self.adjustSize()        

    def walk(self):
        if self.is_sitting or self.is_paused:
            return
        
        if self.frames:
            current_pixmap = self.frames[self.frame_index]

            if self.dx <0:
                from PyQt6.QtGui import QTransform
                current_pixmap = current_pixmap.transformed(QTransform().scale(-1, 1))
            self.cat_label.setPixmap(current_pixmap)
            self.frame_index = (self.frame_index+1)%len(self.frames)

        self.cat_label.adjustSize()
        self.adjustSize()
        self.x+=self.dx

        screen = QApplication.primaryScreen()
        screen_width = screen.geometry().width() if screen else 1400

        if self.x + self.width() >= screen_width:
            self.dx = -3
        elif self.x <= 0:
            self.dx = 3
        
        self.move(self.x, self.y)

    def start_pomodoro(self):
        self.pomo_active = True
        self.pomo_timer.start(1000)
        self.update_pomodoro_display()

    def pause_pomodoro(self):
        self.pomo_active = False
        self.pomo_timer.stop()

    def reset_pomodoro(self):
        self.pomo_timer.stop()
        self.pomo_active = False
        self.pomo_time_left = 25 * 60
        self.update_weather()

    def update_pomodoro_tick(self):
        if self.pomo_time_left > 0:
            self.pomo_time_left -= 1
            self.update_pomodoro_display()
        else:
            self.pomo_timer.stop()
            self.pomo_active = False
            self.bubble.setText("Time's up! Take a break! ☕")
            self.adjustSize()
            self.toggle_sit()  # Make the cat sit when time is up

    def update_pomodoro_display(self):
        minutes = self.pomo_time_left // 60
        seconds = self.pomo_time_left % 60
        self.bubble.setText(f"🐱 Focus: {minutes:02d}:{seconds:02d}")
        self.adjustSize()

    def update_weather(self):
        if self.pomo_active:
            return
        msg = get_weather(LAT,LON)
        self.bubble.setText(f"🐱: {msg}")
        self.adjustSize()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self,event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            new_pos = event.globalPosition().toPoint()- self.drag_position
            self.move(new_pos)
            self.x = new_pos.x()
            self.y = new_pos.y()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.click_start_pos:
            delta = (event.globalPosition().toPoint() - self.click_start_pos).manhattanLength()
            if delta < 5:
                self.toggle_sit()
        self.drag_position = None
        self.click_start_pos = None

    def contextMenuEvent(self, event):
        from PyQt6.QtWidgets import QMenu

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2D3748;
                color: #EDF2F7;
                border: 1px solid #4A5568;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
            QMenu::item:selected {
                background-color: #4A5568;
            }
        """)
        sit_text = "Walk" if self.is_sitting else "Sit"
        sit_action = menu.addAction(sit_text)
        pause_text = "▶ Resume Walk" if self.is_paused else "⏸ Pause Walk"
        pause_action = menu.addAction(pause_text)
        quit_action = menu.addAction("Quit TaskWidget")

        action = menu.exec(event.globalPos())

        if action == sit_action:
            self.toggle_sit()
        elif action == pause_action:
            self.toggle_pause()
        elif action == quit_action:
            QApplication.quit()

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    
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
                ns_window.setLevel_(5) 
        except Exception as e:
            print("Space Behavior Error:", e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    pet = TaskWidget()
    sys.exit(app.exec())