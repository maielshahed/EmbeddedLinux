import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                            QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout)
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import QTimer, QDateTime, QUrl, QThread, pyqtSignal, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
import speech_recognition as sr
import cv2  # OpenCV for camera feed
import MainScreen

# Create a separate thread for voice commands
class VoiceThread(QThread):
    command_detected = pyqtSignal(str)
    listening_status = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self._running = True
        
    def run(self):
        while self._running:
            try:
                with sr.Microphone() as source:
                    self.listening_status.emit(True)
                    audio = self.recognizer.listen(source)
                    text = self.recognizer.recognize_google(audio)
                    self.command_detected.emit(text.lower())
            except:
                pass
            
    def stop(self):
        self._running = False

# Camera thread to capture frames
class CameraThread(QThread):
    frame_captured = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self._running = True
        self.cap = cv2.VideoCapture(0)  # Open the default camera

    def run(self):
        while self._running:
            ret, frame = self.cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_captured.emit(convert_to_Qt_format)
        self.cap.release()

    def stop(self):
        self._running = False
        self.cap.release()

class CarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Smart Control Hub")
        self.setGeometry(0, 0, 1024, 600)
        
        # Initialize main widget and layouts
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.horizontal_layout = QHBoxLayout(self.central_widget)
        
        # Left Panel (Camera Feed)
        self.setup_left_panel()
        
        # Right Panel (Maps)
        self.setup_right_panel()
        
        # Initialize variables
        self.lights_active = False
        self.gps_active = False
        self.map_view = None
        self.camera_thread = None
        
        # Setup components
        self.setup_datetime()
        self.setup_voice_recognition()
        
        # Connect buttons
        self.connect_buttons()

    def setup_left_panel(self):
        self.left_panel = QFrame()
        self.left_panel.setFrameShape(QFrame.StyledPanel)
        self.vertical_layout = QVBoxLayout(self.left_panel)
        self.left_panel.setStyleSheet("""
            QFrame {
                background-color: #1B3435;
                border-radius: 10px;
                color: #fdfffc;  /* Set font color to #fdfffc */
                font-size: 22px;
            }
        """)
        # Date and Time Section
        self.setup_datetime_section()
        
        # Camera Section
        self.setup_camera_section()

        # Voice Control Section
        self.setup_voice_control()
        
        # Control Buttons
        self.setup_control_buttons()
        
        self.horizontal_layout.addWidget(self.left_panel)

    def setup_datetime_section(self):
        self.date_time_frame = QFrame()
        self.date_time_layout = QHBoxLayout(self.date_time_frame)
        
        self.date_label = QLabel("Date:")
        self.day_label = QLabel("Day:")
        
        self.date_time_layout.addWidget(self.date_label)
        self.date_time_layout.addWidget(self.day_label)
        
        self.vertical_layout.addWidget(self.date_time_frame)
        
    def setup_camera_section(self):
        self.camera_frame = QFrame()
        self.camera_frame_layout = QHBoxLayout(self.camera_frame)
        self.camera_label = QLabel("Camera Feed")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_frame_layout.addWidget(self.camera_label)
        self.vertical_layout.addWidget(self.camera_frame)

    def setup_voice_control(self):
        self.voice_control_frame = QFrame()
        self.voice_layout = QVBoxLayout(self.voice_control_frame)
        
        self.mic_button = QPushButton()
        self.mic_button.setMinimumSize(64, 64)
        self.mic_button.setIcon(QIcon("speakerIcon.png"))
        self.mic_button.setObjectName("micButton")
        self.mic_button.setStyleSheet("""
            QPushButton#micButton {
                background-color: #3498db;
                border-radius: 32px;
            }
            QPushButton#micButton:hover {
                background-color: #ff9933;
            }
        """)
        self.voice_layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)
        self.vertical_layout.addWidget(self.voice_control_frame)

    def setup_control_buttons(self):
        self.control_buttons_frame = QFrame()
        self.control_buttons_layout = QGridLayout(self.control_buttons_frame)
        
        self.lights_button = QPushButton("Lights Off")
        self.gps_button = QPushButton("GPS Off")
        self.camera_button = QPushButton("Open Camera")
        self.back_button = QPushButton("Back")

        button_style = """
            QPushButton {
                background-color: #093A3E;
                color: #7E9D9E;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
                border: 2px solid #7E9D9E;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                background-color: #1B3435;
                font-size: 14px;
                padding: 10px;
                border-radius: 8px;
                border: 2px solid #7E9D9E;
                transition: all 0.3s ease;
            }
            QPushButton:pressed {
                background-color: #ED6C02;
                border: 2px solid #ff7b00;
            }
            QPushButton:checked {
                background-color: #ED6C02;
                border: 2px solid #ff7b00;
            }
        """
        self.lights_button.setStyleSheet(button_style)
        self.gps_button.setStyleSheet(button_style)
        self.camera_button.setStyleSheet(button_style)
        self.back_button.setStyleSheet(button_style)

        self.control_buttons_layout.addWidget(self.lights_button, 0, 0)
        self.control_buttons_layout.addWidget(self.gps_button, 0, 1)
        self.control_buttons_layout.addWidget(self.camera_button, 1, 0)
        self.control_buttons_layout.addWidget(self.back_button, 1, 1)

        self.vertical_layout.addWidget(self.control_buttons_frame)

    def setup_right_panel(self):
        self.right_panel = QFrame()
        self.right_panel.setMinimumSize(400, 0)
        self.right_panel.setStyleSheet("""
            QFrame {
                background-color: #1B3435;
                border-radius: 10px;
            }
        """)
        self.right_layout = QVBoxLayout(self.right_panel)
        
        # Maps Section
        self.maps_frame = QFrame()
        self.maps_layout = QVBoxLayout(self.maps_frame)
        self.right_layout.addWidget(self.maps_frame)
        
        self.horizontal_layout.addWidget(self.right_panel)

    def setup_datetime(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.update_datetime()

    def update_datetime(self):
        current_datetime = QDateTime.currentDateTime()
        date_text = current_datetime.toString("dd-MM-yyyy")
        day_text = current_datetime.toString("dddd")
        self.date_label.setText(f"Date: {date_text}")
        self.day_label.setText(f"Day: {day_text}")

    def setup_voice_recognition(self):
        self.voice_thread = VoiceThread()
        self.voice_thread.command_detected.connect(self.handle_voice_command)
        self.voice_thread.listening_status.connect(self.update_mic_status)
        self.voice_thread.start()

    def connect_buttons(self):
        self.lights_button.clicked.connect(self.toggle_lights)
        self.gps_button.clicked.connect(self.toggle_gps)
        self.camera_button.clicked.connect(self.toggle_camera)
        self.back_button.clicked.connect(self.back_to_main)

    def handle_voice_command(self, command):
        if "lights on" in command:
            self.toggle_lights()
        elif "lights off" in command:
            self.toggle_lights()
        elif "gps on" in command:
            self.toggle_gps()
        elif "gps off" in command:
            self.toggle_gps()

    def update_mic_status(self, is_listening):
        self.mic_button.setStyleSheet(
            f"QPushButton#micButton {{ background-color: {'#ff9933' if is_listening else '#3498db'}; border-radius: 32px; }}"
        )

    def toggle_lights(self):
        self.lights_active = not self.lights_active
        self.lights_button.setText("Lights On" if self.lights_active else "Lights Off")
        if not self.lights_active:
            self.camera_label.clear()
            if self.camera_thread:
                self.camera_thread.stop()
                self.camera_thread.wait()
                self.camera_thread = None

    def toggle_gps(self):
        self.gps_active = not self.gps_active
        self.gps_button.setText("GPS On" if self.gps_active else "GPS Off")
        if self.gps_active:
            self.setup_google_maps()
        else:
            if self.map_view:
                self.map_view.setParent(None)
                self.map_view = None

    def toggle_camera(self):
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None
            self.camera_label.clear()
        else:
            self.start_camera_feed()

    def setup_google_maps(self):
        if not self.map_view:
            self.map_view = QWebEngineView()
            self.maps_layout.addWidget(self.map_view)
            self.map_view.setUrl(QUrl("https://www.google.com/maps"))

    def start_camera_feed(self):
        self.camera_thread = CameraThread()
        self.camera_thread.frame_captured.connect(self.update_camera_feed)
        self.camera_thread.start()

    def update_camera_feed(self, image):
        self.camera_label.setPixmap(QPixmap.fromImage(image))

    def back_to_main(self):
        self.main_window = MainScreen.MainWindow()
        self.main_window.show()
        self.close()

    def closeEvent(self, event):
        self.voice_thread.stop()
        self.voice_thread.wait()
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
        self.timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarWindow()
    window.show()
    sys.exit(app.exec_())