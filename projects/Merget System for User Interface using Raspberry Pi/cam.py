import cv2
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

class RoomWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Home - Rooms")
        self.setGeometry(100, 100, 1024, 600)
        self.setStyleSheet("background-color: #001819;")

        # Main widget container
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QVBoxLayout(self.central_widget)

        # Video display
        self.video_label = QLabel(self)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.video_label)

        # Camera Button
        self.camera_button = QPushButton("Start Camera", self)
        self.camera_button.clicked.connect(self.toggle_camera)
        self.layout.addWidget(self.camera_button)

        # Camera variables
        self.camera = None
        self.timer = QTimer()

    def toggle_camera(self):
        """ Start/Stop Camera on button press """
        if self.camera is None:  # Start camera
            self.camera = cv2.VideoCapture(0)  # Open camera
            if not self.camera.isOpened():
                self.camera = None
                return
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
            self.camera_button.setText("Stop Camera")
        else:  # Stop camera
            self.timer.stop()
            self.camera.release()
            self.camera = None
            self.video_label.clear()
            self.camera_button.setText("Start Camera")

    def update_frame(self):
        """ Capture and display camera frames """
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert color
            h, w, ch = frame.shape
            q_image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_image))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoomWindow()
    window.show()
    sys.exit(app.exec_())
