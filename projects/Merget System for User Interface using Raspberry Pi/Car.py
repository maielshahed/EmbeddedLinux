import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,QWidget, 
                            QVBoxLayout, QLabel,QFrame,QHBoxLayout,QGridLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QDateTime, QUrl, QThread, pyqtSignal, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
import speech_recognition as sr

import MainScreen

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
        
        # Left Panel
        self.setup_left_panel()
        
        # Right Panel (Maps)
        self.setup_right_panel()
        
        # Initialize variables
        self.BLUE_COLOR = "#1B3435"
        self.ORANGE_COLOR = "#ff9933"
        self.lights_active = False
        self.gps_active = False
        self.map_view = None
        
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
        
        self.lights_on_button = QPushButton("Lights On")
        self.gps_on_button = QPushButton("GPS On")
        self.lights_off_button = QPushButton("Lights Off")
        self.gps_off_button = QPushButton("GPS Off")

    def setup_control_buttons(self):
            self.control_buttons_frame = QFrame()

            self.control_buttons_layout = QGridLayout(self.control_buttons_frame)

            

            self.lights_on_button = QPushButton("Lights On")

            self.gps_on_button = QPushButton("GPS On")

            self.lights_off_button = QPushButton("Lights Off")

            self.gps_off_button = QPushButton("GPS Off")

            # Custom stylesheet for control buttons


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

                    background-color: #ED6C02;  /* Orange when pressed */

                    border: 2px solid #ff7b00;

                }


                QPushButton:checked {

                    background-color: #ED6C02;  /* Orange when checked */

                    border: 2px solid #ff7b00;

                }


            """

            # Define button styles as class attributes

            self.button_style_default = """

                QPushButton {

                    background-color: #093A3E;

                    color: #7E9D9E;

                    font-size: 16px;

                    padding: 10px;

                    border-radius: 8px;

                    border: 2px solid #7E9D9E;

                }

            """

            

            self.button_style_active = """

                QPushButton {

                    background-color: #ED6C02;

                    color: white;

                    font-size: 16px;

                    padding: 10px;

                    border-radius: 8px;

                    border: 2px solid #ff7b00;

                }

            """
                # Back button
            self.back_button = QPushButton("Back", self)
            self.back_button.setStyleSheet(button_style)
            self.back_button.clicked.connect(self.back_to_main)
            
            self.control_buttons_layout.addWidget(self.lights_on_button, 0, 0)
            self.lights_on_button.setStyleSheet(button_style)

            self.control_buttons_layout.addWidget(self.gps_on_button, 0, 1)
            self.gps_on_button.setStyleSheet(button_style)

            self.control_buttons_layout.addWidget(self.lights_off_button, 1, 0)
            self.lights_off_button.setStyleSheet(button_style)

            self.control_buttons_layout.addWidget(self.gps_off_button, 1, 1)
            self.gps_off_button.setStyleSheet(button_style)

            self.control_buttons_layout.addWidget(self.back_button, 2, 0, 1, 2)
            self.vertical_layout.addWidget(self.control_buttons_frame)

    def setup_right_panel(self):
        self.maps_frame = QFrame()
        self.maps_frame.setMinimumSize(400, 0)
        self.maps_frame.setStyleSheet("""
            QFrame {
                background-color: #1B3435;
                border-radius: 10px;
            }
        """)
        self.maps_layout = QVBoxLayout(self.maps_frame)
        self.horizontal_layout.addWidget(self.maps_frame)

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
        self.lights_on_button.clicked.connect(lambda: self.handle_lights("on"))
        self.lights_off_button.clicked.connect(lambda: self.handle_lights("off"))
        self.gps_on_button.clicked.connect(lambda: self.handle_gps("on"))
        self.gps_off_button.clicked.connect(lambda: self.handle_gps("off"))

    def handle_voice_command(self, command):
        if "lights on" in command:
            self.handle_lights("on")
            
        elif "lights off" in command:
            self.handle_lights("off")
        elif "gps on" in command:
            self.handle_gps("on")
        elif "gps off" in command:
            self.handle_gps("off")

    def update_mic_status(self, is_listening):
        self.mic_button.setStyleSheet(
            f"QPushButton#micButton {{ background-color: {'#ff9933' if is_listening else '#3498db'}; border-radius: 32px; }}"
        )

    def handle_lights(self, state):

        if state == "on":

            # Activate Lights On button

            self.lights_on_button.setStyleSheet(self.button_style_active)

            self.lights_off_button.setStyleSheet(self.button_style_default)

            

            # Disable Lights On button and enable Lights Off button

            self.lights_on_button.setEnabled(False)

            self.lights_off_button.setEnabled(True)

            

            self.lights_active = True

        else:

            # Activate Lights Off button

            self.lights_off_button.setStyleSheet(self.button_style_active)

            self.lights_on_button.setStyleSheet(self.button_style_default)

            

            # Disable Lights Off button and enable Lights On button

            self.lights_off_button.setEnabled(False)

            self.lights_on_button.setEnabled(True)

            

            self.lights_active = False

    def handle_gps(self, state):

        if state == "on":

            # Activate GPS On button

            self.gps_on_button.setStyleSheet(self.button_style_active)

            self.gps_off_button.setStyleSheet(self.button_style_default)

            

            # Disable GPS On button and enable GPS Off button

            self.gps_on_button.setEnabled(False)

            self.gps_off_button.setEnabled(True)

            

            self.gps_active = True

            self.setup_google_maps()

        else:

        # Activate GPS Off button

            self.gps_off_button.setStyleSheet(self.button_style_active)

            self.gps_on_button.setStyleSheet(self.button_style_default)

            

            # Disable GPS Off button and enable GPS On button

            self.gps_off_button.setEnabled(False)

            self.gps_on_button.setEnabled(True)

            

            self.gps_active = False

            

            if self.map_view:

                self.map_view.setParent(None)

                self.map_view = None

    def setup_google_maps(self):
        if not self.map_view:
            self.map_view = QWebEngineView()
            self.maps_layout.addWidget(self.map_view)
            self.map_view.setUrl(QUrl("https://www.google.com/maps"))
    def back_to_main(self):
        self.main_window = MainScreen.MainWindow()
        self.main_window.show()
        self.close()

    def closeEvent(self, event):
        self.voice_thread.stop()
        self.voice_thread.wait()
        self.timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarWindow()
    window.show()
    sys.exit(app.exec_())
