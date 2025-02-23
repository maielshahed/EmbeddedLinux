
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                            QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout, QSizePolicy)
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import QTimer, QDateTime, QUrl, QThread, pyqtSignal, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtMultimediaWidgets import QVideoWidget

import speech_recognition as sr
import cv2  # OpenCV for camera feed
import MainScreen
import numpy as np

class LaneDetector:
    def __init__(self):
        pass

    def process_frame(self, frame):
        roi = self.region_of_interest(frame)
        edges = self.detect_edges(roi)
        lines = self.detect_lanes(edges)
        lane_image = self.draw_lanes(frame, lines)
        return lane_image

    def region_of_interest(self, frame):
        height, width = frame.shape[:2]
        mask = np.zeros_like(frame)
        
        # Define a trapezoidal region focusing on the road
        region = np.array([
            [(0, height), (width, height), (width//2 + 100, height//2), (width//2 - 100, height//2)]
        ], dtype=np.int32)
        
        cv2.fillPoly(mask, region, (255, 255, 255))
        return cv2.bitwise_and(frame, mask)

    def detect_edges(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        return edges

    def detect_lanes(self, edges):
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=100, maxLineGap=50)
        return lines

    def draw_lanes(self, frame, lines):
        if lines is None:
            return frame
        
        left_lines, right_lines = [], []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1) if (x2 - x1) != 0 else 0
            if 0.5 < abs(slope) < 2:  # Filtering out horizontal or steep lines
                if slope < 0:
                    left_lines.append((x1, y1, x2, y2))
                else:
                    right_lines.append((x1, y1, x2, y2))
        
        left_lane = self.fit_lane_curve(left_lines, frame.shape)
        right_lane = self.fit_lane_curve(right_lines, frame.shape)
        
        if left_lane is not None:
            cv2.polylines(frame, [left_lane], isClosed=False, color=(0, 255, 0), thickness=5)
        if right_lane is not None:
            cv2.polylines(frame, [right_lane], isClosed=False, color=(0, 255, 0), thickness=5)
        
        return frame

    def fit_lane_curve(self, lines, shape):
        if len(lines) == 0:
            return None
        
        x_coords, y_coords = [], []
        for x1, y1, x2, y2 in lines:
            x_coords.extend([x1, x2])
            y_coords.extend([y1, y2])
        
        poly_fit = np.polyfit(y_coords, x_coords, 2)
        y_vals = np.linspace(shape[0]//2, shape[0], num=50)
        x_vals = np.polyval(poly_fit, y_vals)
        
        lane_points = np.array([np.transpose(np.vstack([x_vals, y_vals]))], dtype=np.int32)
        return lane_points
        
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
        self.cap = cv2.VideoCapture(0)  

    def run(self):
        while self._running:
            ret, frame = self.cap.read()
            if ret:
                processed_frame = self.detect_lanes(frame)
                rgb_image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_captured.emit(qt_image)
        self.cap.release()

    def detect_lanes(self, frame):
        height, width = frame.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detect edges using Canny
        edges = cv2.Canny(blur, 50, 150)
        
        # Define a region of interest (ROI) to focus on road lanes
        mask = np.zeros_like(edges)
        roi_vertices = np.array([[(100, height), (width // 2 - 50, height // 2 + 50),
                                  (width // 2 + 50, height // 2 + 50), (width - 100, height)]],
                                dtype=np.int32)
        cv2.fillPoly(mask, roi_vertices, 255)
        masked_edges = cv2.bitwise_and(edges, mask)
        
        # Detect lane lines using Hough Transform
        lines = cv2.HoughLinesP(masked_edges, 1, np.pi / 180, 50, minLineLength=100, maxLineGap=50)
        
        # Filter lines based on slope to detect only road lanes
        left_lane = []
        right_lane = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                slope = (y2 - y1) / (x2 - x1) if x2 - x1 != 0 else 999  # Avoid division by zero
                
                if 0.5 < abs(slope) < 2.0:  # Filter nearly vertical lines (valid lane slopes)
                    if slope < 0:  # Left lane (negative slope)
                        left_lane.append((x1, y1, x2, y2))
                    else:  # Right lane (positive slope)
                        right_lane.append((x1, y1, x2, y2))
        
        # Draw filtered lane lines
        for lane in [left_lane, right_lane]:
            for x1, y1, x2, y2 in lane:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
        
        return frame

    def stop(self):
        self._running = False
        self.cap.release()


class CarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Smart Control Hub")
        self.setFixedSize(1024, 600)

        
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
        self.camera_thread = False
        
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
                font-size: 16px;
            }
             QLabel#textBorder {
                border: 2px solid #fdfffc;
                border-radius: 5px;
                padding: 0px;
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
    # Assign the object name to apply the #textBorder style
        self.date_label.setObjectName("textBorder")
        self.day_label.setObjectName("textBorder")   

        self.date_time_layout.addWidget(self.date_label)
        self.date_time_layout.addWidget(self.day_label)
        
        self.vertical_layout.addWidget(self.date_time_frame)

        # Create a label to display the ultrasonic sensor result
        self.ultrasonic_result_label = QLabel("Ultrasonic Result: 0 cm")  # Default text
        self.ultrasonic_result_label.setObjectName("textBorder")  # Apply the same border style
        self.ultrasonic_result_label.setAlignment(Qt.AlignCenter)  # Center-align the text
        
        # Add the ultrasonic result label to the main layout
        self.vertical_layout.addWidget(self.ultrasonic_result_label)
     
    

    def setup_camera_section(self):
        self.camera_frame = QFrame()
        self.camera_frame_layout = QHBoxLayout(self.camera_frame)
        
        # Create a QLabel to display the video feed (camera label)
        self.camera_label = QLabel("Camera Feed")
        self.camera_label.setAlignment(Qt.AlignCenter)
        
        # Create a video widget (QVideoWidget) to display the camera feed
        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Ensure it scales with the window
        
        # Add the video widget to the layout
        self.camera_frame_layout.addWidget(self.video_widget)
    
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
        elif "camera on" in command:
            self.toggle_camera()
        elif "camera off" in command:
            self.toggle_camera()

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
        #self.camera_thread = not self.camera_thread
        #self.gps_button.setText("Start Camera" if self.camera_active else "Close Camera")
  
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_button.setText("Start Camera" )
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None
            self.camera_label.clear()
        else:
            self.camera_button.setText("Stop Camera" )

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

    def update_camera_feed(self, qt_image):
        self.camera_label.setPixmap(QPixmap.fromImage(qt_image))


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