
import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton,QVBoxLayout, QLabel 

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize,QUrl

from PyQt5.QtMultimedia import QCamera, QCameraInfo

from PyQt5.QtWebEngineWidgets import QWebEngineView
import paho.mqtt.client as mqtt
from PyQt5.QtMultimediaWidgets import QVideoWidget

import HomeScreen


class MQTTClient:
    def __init__(self, broker, port, topic, username, password):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        #self.client = mqtt.Client()
        self.client.username_pw_set(username=username, password=password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.start()
    def on_connect(self, client, userdata, flags, rc, properties=None):
        print(f"Connected to MQTT broker with code {rc}.")
        self.client.subscribe(self.topic)
        
    def on_message(self, client, userdata, msg):
        self.handle_mqtt_message(msg)

    def handle_mqtt_message(self, msg):
        print(f"Received message on {msg.topic}: {msg.payload.decode('utf-8')}")

    def publish_message(self, message):
        self.client.publish(self.topic, message)
        print(f"Published message: {message}")

    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
    


# --------------------- Room Home ---------------------
class RoomWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(0, 0, 1024, 600)
        self.setStyleSheet("background-color: #001819;")


    # Initialize OpenCV video capture
        self.cap = cv2.VideoCapture(0)  # 0 is typically the default camera

        # Set up a timer to fetch frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        # Create a QLabel to display the camera feed
        self.video_label = QLabel(self)
                # Set fixed size for the video label
        label_width = 512
        label_height = 300
        self.video_label.setFixedSize(label_width, label_height)

        # Calculate position for bottom-right corner with a margin
        #margin = 10
        #x = self.width() - label_width - margin
        #y = self.height() - label_height - margin

        # Set the geometry of the video label
        #self.video_label.setGeometry(x, y, label_width, label_height)
        self.video_label.setStyleSheet("border: 2px solid #FFD700;")
        self.video_label.setVisible(False)  # Initially hidden

        #Back button home
        self.Home_button = self.create_toggle_button("Home", "icons_back.png", 20, 20)
        self.Home_button.clicked.connect(self.back_to_home)
        
        self.mqtt_client = MQTTClient(
        broker='b37.mqtt.one',
        port=1883,
        topic='35celv8628/HomeControl',
        username='35celv8628',
        password='890fijpqtw'
    )
#---------------------------family----------------------------------

    

        self.Family_button = QPushButton("Family", self)
        self.Family_button.setGeometry(120, 20, 90, 100)
        self.Family_button.setStyleSheet("background-color: transparent;  color : #7E9D9E; ")
        self.Floor_button = self.create_toggle_button("Floor", "icons_led.png", 220, 20)
        self.dining_room_button = self.create_toggle_button("dining room", "icons_dining_room.png", 320, 20)
        self.kitchen_button = self.create_toggle_button("kitchen", "icons-kitchen.png", 420, 20)
       

#---------------------------master----------------------------------


        self.master_button = QPushButton("Master", self)
        self.master_button.setGeometry(120, 130, 90, 100)
        self.master_button.setStyleSheet("background-color: transparent;  color : #7E9D9E; ")
        self.Bedroom_button = self.create_toggle_button("Bedroom", "icons_bed.png", 220, 130)
        self.shower_button = self.create_toggle_button("shower", "icons_shower.png", 320, 130)
        self.Clothes_room_button = self.create_toggle_button("Clothes", "icons_womens.png", 420, 130)
        self.Fan_button = self.create_toggle_button("Fan", "icons_fan.png", 520, 130)



#---------------------------garage----------------------------------

        self.garage_button = QPushButton("Garage", self)
        self.garage_button.setGeometry(120, 240, 90, 100)
        self.garage_button.setStyleSheet("background-color: transparent;  color : #7E9D9E; ")
        self.garagdoor_button = self.create_toggle_button("Garage Door", "icons_garage.png", 220, 240)
        self.led_button = self.create_toggle_button("LED", "icons_light.png", 320, 240)
        self.Clothes_room_button = self.create_toggle_button("Door", "icons-door.png", 420, 240)


#---------------------------------------cameraButton-------------------------------------------------------


# زر تشغيل/إيقاف الكاميرا
        self.cameraButton = self.create_toggle_button("Camera", "camera.png", 20, 350)
        self.cameraButton.clicked.connect(self.toggle_camera)

         # Create the hint label in the setup/init function
        self.camera_hint_label = QLabel("Camera Entrance", self)
        self.camera_hint_label.setStyleSheet("background-color: rgba(0, 0, 0, 100); color: white; font-size: 20px; padding: 10px;")
        self.camera_hint_label.setAlignment(Qt.AlignCenter)
        self.camera_hint_label.setVisible(False)  # Initially hidden

        # Adjust the label size based on the content
        self.camera_hint_label.adjustSize()  # This ensures the label resizes to fit the text

        # Position the hint label at the bottom-left corner (1024 - 512, 600 - 300)
        self.camera_hint_label.move(1024 - 512, 600 - 300)  # Position it at the bottom-left corner



#----------------------------------------------RadioPlayer_button---------------------------------------------------------------
       # Radio play button
        self.playButton = self.create_toggle_button("Radio", "Play_Radio.png",20,130)
        self.playButton.clicked.connect(self.toggleRadio)

     
        # Hide browser button
        self.hideButton = self.create_toggle_button("Hide Radio", "Hide_Radio.png",20,240)
        self.hideButton.clicked.connect(self.hideRadio)
        self.hideButton.setEnabled(False)  # Disable it at first until it starts running


              # Add the browser inside the window, specifying its size and location
# Built-in browser (hidden at first)
        self.browser = QWebEngineView()
        self.browser.hide()

    def toggle_camera(self):
        """Start/Stop the camera when the button is pressed."""
        if self.cameraButton.isChecked():
            self.video_label.setVisible(True)  # Show video label (camera feed)
            self.camera_hint_label.setVisible(True)  # Show camera entrance hint
            self.timer.start(30)  # Update every 30 ms
            self.mqtt_client.publish_message("Camera ON")
        else:
            self.timer.stop()
            self.video_label.setVisible(False)  # Hide video label (camera feed)
            self.camera_hint_label.setVisible(False)  # Hide the camera entrance hint
            self.mqtt_client.publish_message("Camera OFF")

    def update_frame(self):
        # Set the desired width and height for the resized frame (you can change these values as needed)
        frame_width = 512  # Width for the resized frame
        frame_height = 300  # Height for the resized frame

        # Set the position where you want the frame (x and y values can be adjusted)
        pos_x = 1024 - frame_width  # Position X (adjust as needed)
        pos_y = 600 - frame_height  # Position Y (adjust as needed)

        ret, frame = self.cap.read()
        if ret:
            # Resize the frame to the specified size (frame_width x frame_height)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame, (frame_width, frame_height))

            # Get the dimensions of the resized frame
            h, w, ch = frame_resized.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_resized.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Scale the image to fit the QLabel
            scaled_qt_image = qt_image.scaled(self.video_label.size(), Qt.KeepAspectRatio)

            # Set the pixmap to display the frame on the QLabel
            self.video_label.setPixmap(QPixmap.fromImage(scaled_qt_image))

            # Position the QLabel at the specified position (bottom-left corner, or whatever you choose)
            self.video_label.move(pos_x, pos_y)  # Move the QLabel to the desired position
    '''
    def update_frame(self):
        """Capture frame from camera and display it."""
        ret, frame = self.cap.read()
        if ret:
            # Convert the frame to RGB format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Get the frame dimensions
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            # Convert to QImage
            q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            # Display the image in the QLabel
            self.video_label.setPixmap(QPixmap.fromImage(q_image))
'''
    def closeEvent(self, event):
        """Handle the window close event."""
        self.timer.stop()
        self.cap.release()
        event.accept()
        

    def toggleRadio(self):
        """Turn the radio on or off when pressing the same button"""
        if self.playButton.isChecked():
            # turn on the radio
            
            self.browser.setUrl(QUrl("https://surahquran.com/Radio-Quran-Cairo.html"))
            self.browser.show()
            self.hideButton.setEnabled(True) 
        else:
            # stop the radio
            self.browser.setUrl(QUrl())  # Stop downloading
            self.browser.hide()


    def stopRadio(self):
        """stop the radio"""
        self.browser.setUrl(QUrl())  # Stop downloading
        self.browser.hide()

# Re-enable the power button and disable the stop and hide buttons.
        self.playButton.setEnabled(True)
        self.hideButton.setEnabled(False)
 
    def hideRadio(self):
        """Hide browser without stopping radio    """
        self.browser.hide()
        self.hideButton.setEnabled(False)



   


#--------------------------------------------------------------------------------------------------------------


    def create_toggle_button(self, text, icon_path, x, y):
        """Toggle """
        button = QPushButton(self)
        button.setGeometry(x, y, 90, 100)
        button.setCheckable(True)  # To make the button toggleable
        button.setStyleSheet("""
            QPushButton {
                
                background-color: #1B3435;
                color: #34351B;
                text-align: center;
                border:none; 
                
            }
            
                             
            QPushButton:hover {
                background-color: #3A4F4F;  /* mouse hover effect*/
            }
            QPushButton:checked {
                color: #001819;
                background-color: #ED6C02;  /* Change background color on click*/       
                border: 2px solid #FFD700;  /* Change frame color on click*/

            }
 

        """)

        layout = QVBoxLayout()

        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(50, 50)))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")  # remove dark background

        # **Create text**
        label = QLabel(text)
        label.setStyleSheet("color: #7E9D9E; background: transparent;")
        label.setAlignment(Qt.AlignCenter)

       
        
        layout.addWidget(label) 
        layout.addWidget(icon_label)  

        #button.clicked.connect(lambda: mqtt_client.publish_message(f"{text} ON") if button.isChecked() else mqtt_client.publish_message(f"{text} OFF"))
  
        button.setLayout(layout)
        button.clicked.connect(lambda: self.mqtt_client.publish_message(f"{text} ON") if button.isChecked() else self.mqtt_client.publish_message(f"{text} OFF"))
        return button

       

#Back button home
    def back_to_home(self):
        self.main_window = HomeScreen.HomeWindow()
        self.main_window.show()
        self.close()
        MQTTClient.stop(self.mqtt_client)


# Event to close the window when pressing a key on the keyboard
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # When you press the Esc button
            self.close()                 # Close window
        elif event.key() == Qt.Key_Q:    # When you press the Q button
            self.close()                 # Close the window also.
        else:
            super().keyPressEvent(event)  # Virtual event implementation


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoomWindow()
    window.show()
   
    sys.exit(app.exec_())




