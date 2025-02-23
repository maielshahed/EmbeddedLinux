import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                            QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout)
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import QTimer, QDateTime, QUrl, QThread, pyqtSignal, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
import speech_recognition as sr
import cv2  # OpenCV for camera feed
import MainScreen
import numpy as np

#***********************************************************************************************************//
#                                               begain of class LaneDetector
#***********************************************************************************************************//
class LaneDetector:
    def __init__(self):
        pass
    def check_car_position(self, frame):
        #extract the original frame dimensions
        height, width = frame.shape[:2]
 


        # Define the region of interest (area between guidelines)        
        left_boundary = int(width * 0.35)                   #Sets the left boundary of the ROI to 35% of the frame's width.
        right_boundary =  int(width * 0.65)              #Sets the right boundary to 65% of the frame's width
        top_boundary =  int(height * 0.5)               #Sets the top boundary to 50% of the frame's height.
        bottom_boundary = height                                                    #Sets the bottom boundary to the full height of the frame.
        
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to detect dark objects (assuming car is darker)
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        
        # Get the region of interest
        roi = thresh[top_boundary:bottom_boundary, left_boundary:right_boundary]
        
        # Calculate the percentage of non-zero pixels in the ROI
        non_zero_pixels = cv2.countNonZero(roi)
        total_pixels = roi.shape[0] * roi.shape[1]
        occupation_ratio = non_zero_pixels / total_pixels
        
        # Return True if there's significant object detection in the ROI
        return occupation_ratio > 0.2  # Adjust this threshold as needed return boolen
    def process_frame(self, frame):
        # Add parking guidelines
        frame_with_guidelines = self.draw_parking_guidelines(frame)
        
        # Check if car is within guidelines
        is_car_inside = self.check_car_position(frame)
        
        return frame_with_guidelines, is_car_inside

    def draw_parking_guidelines(self, frame):
        #extract the original frame dimensions

        height, width = frame.shape[:2]
    
        # Define the guidelines points
        left_top = (int(width * 0.35), int(height * 0.6))        # Adjusted from 0.15 to 0.35
        right_top = (int(width * 0.65), int(height * 0.6))       # Adjusted from 0.85 to 0.65
        left_bottom = (int(width * 0.2), height)                 # Adjusted from 0 to 0.2
        right_bottom = (int(width * 0.8), height)                # Adjusted from width to 0.8
        
        # Center vertical line
        center_top = (int(width * 0.5), int(height * 0.6))      # Adjusted center line
        center_bottom = (int(width * 0.5), height)
                
        # Check car position to determine line color
        is_car_inside = self.check_car_position(frame)          #true or false
        line_color = (5, 168, 19) if is_car_inside else (0, 32, 232)  # Green if is_car_inside, Red otherwise        

        # Draw the guidelines with dynamic color
        cv2.line(frame, left_bottom , left_top , line_color, 2)  # Left line with thickness 3
        cv2.line(frame, right_bottom ,right_top , line_color, 2)  # Right line with thickness 3
        cv2.line(frame, center_bottom ,center_top , (255, 0, 0), 2)  # Center line (always blue) with thickness 3
        
        # Draw horizontal reference lines with dynamic color top and buttom lines
        # Draw horizontal reference lines

        cv2.line(frame, (int(width * 0.2), int(height * 0.6)),  (int(width * 0.8), int(height * 0.6)), line_color, 2)  # Top line

        cv2.line(frame, (int(width * 0.2), int(height * 0.8)),  (int(width * 0.8), int(height * 0.8)), line_color, 2)  # Bottom line
        #cv2.line(frame_copy, (0, int(height * 0.5)), (width, int(height * 0.5)), line_color, 3)
        #cv2.line(frame_copy, (0, int(height * 0.7)), (width, int(height * 0.7)), line_color, 3)
        
        return frame

    
#***********************************************************************************************************//
#                                               end of class LaneDetector
#***********************************************************************************************************//


#***********************************************************************************************************//
#                                               start of class VoiceThread
#***********************************************************************************************************//
# Create a separate thread for voice commands
class VoiceThread(QThread):
    command_detected = pyqtSignal(str)                  #var store the detected voice command
    listening_status = pyqtSignal(bool)                 #boolean variable return true if it listen to mic, false if not
    
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
        self.quit()
        self.wait()

#***********************************************************************************************************//
#                                               end of class VoiceThread
#***********************************************************************************************************//


#***********************************************************************************************************//
#                                               start of class CameraThread
#***********************************************************************************************************//
# Camera thread to capture frames
class CameraThread(QThread):
    frame_captured = pyqtSignal(QImage)                 # Signal to send processed frames
    car_position_changed = pyqtSignal(bool)             # Signal to send car position status

    def __init__(self, video_path):  #constructor
        super().__init__()
        self._running = True
        #Initialize video capture
        self.cap = cv2.VideoCapture(video_path)
        #create lane detector object
        self.detector = LaneDetector()

    def run(self):
        while self._running:
            #read frame from the source(camera/video)
            ret, frame = self.cap.read()        
            #if frame captured 
            if ret:
                # Flip the image horizontally to mirror the view
                #frame = cv2.flip(frame, 1)
                
                # Process frame with parking guidelines and get car position
                processed_frame, is_car_inside = self.detector.process_frame(frame)
                
                # Emit/send car position status to main thread
                self.car_position_changed.emit(is_car_inside)
                
                # Convert to RGB for Qt
                rgb_image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_captured.emit(qt_image)
            else:
                self._running = False
        self.cap.release()

    def stop(self):
        self._running = False
        self.cap.release()



#***********************************************************************************************************//
#                                               end of class CameraThread
#***********************************************************************************************************//

#***********************************************************************************************************//
#                                               start of class CarWindow
#***********************************************************************************************************//
class CarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Smart Control Hub")
        #self.setGeometry(0, 0, 1024, 600)
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
        self.camera_thread = None
        
        # Setup components
        self.setup_datetime()
        self.setup_voice_recognition()
        
        # Connect buttons
        self.connect_buttons()
#----------------------------------------------------------------------------------------//        
        # Add keyboard button in bottom-right corner---> still need modification
        self.setup_keyboard_button()      
    def setup_keyboard_button(self):
        # Create keyboard button
        self.keyboard_button = QPushButton("⌨", self)
        self.keyboard_button.setFixedSize(40, 40)  # Small button size
        self.keyboard_button.setStyleSheet("""
            QPushButton {
                background-color: #093A3E;
                color: #7E9D9E;
                border-radius: 20px;
                border: 2px solid #7E9D9E;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #1B3435;
            }
            QPushButton:pressed {
                background-color: #ED6C02;
                border: 2px solid #ff7b00;
            }
        """)      
        # Position the button in bottom-right corner
        self.keyboard_button.move(
            self.width() - self.keyboard_button.width() - 10,  # 10px from right
            self.height() - self.keyboard_button.height() - 10  # 10px from bottom
        )
        # Connect button to keyboard toggle
        #self.keyboard_button.clicked.connect(self.toggle_keyboard)
        #self.keyboard_process = None
#----------------------------------------------------------------------------------------//

    #function set container for the left panel
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

    #function set container for the date/day text,value
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

        # Create a label to display the command voice
        self.Command_Voice_Label = QLabel("command voice: lights on--light off\nCamera on--Camera off\nGPS on-s-GPS off")  # Default text
        self.Command_Voice_Label.setObjectName("textBorder")  # Apply the same border style
        self.Command_Voice_Label.setAlignment(Qt.AlignCenter)  # Center-align the text
        
        # Add the Command voice label to the main layout
        self.vertical_layout.addWidget(self.Command_Voice_Label)

    #function set container for the camera
    def setup_camera_section(self):
        self.camera_frame = QFrame()
        self.camera_frame_layout = QHBoxLayout(self.camera_frame)
        self.camera_label = QLabel("Reverse Camera")
        self.camera_label.setAlignment(Qt.AlignLeft)
        camera_width=int(500)
        camera_height=int(245)
        self.camera_label.setFixedSize(camera_width, camera_height)
        self.camera_frame_layout.addWidget(self.camera_label)
        self.vertical_layout.addWidget(self.camera_frame)
        self.camera_label.setStyleSheet(
            """
            QLabel {
                border: 3px solid #FFD700;              /*Yellow border by default*/
                border-radius: 10px;
                background-color: #000000;
            }
        """)

    #function set container for the speaker
    def setup_voice_control(self):
        self.voice_control_frame = QFrame()
        self.voice_layout = QVBoxLayout(self.voice_control_frame)
        
        self.mic_button = QPushButton()
        self.mic_button.setMinimumSize(35, 35)
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
    
    #function set container for the control buttons
    def setup_control_buttons(self):
        self.control_buttons_frame = QFrame()
        self.control_buttons_layout = QGridLayout(self.control_buttons_frame)
        
        self.lights_button = QPushButton("Lights")
        self.gps_button = QPushButton("GPS")
        self.camera_button = QPushButton("Camera")
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
                color:#000000

            }
            QPushButton:checked {
                background-color: #ED6C02;
                border: 2px solid #ff7b00;
                color:#000000
            }
        """
        #apply stylesheet to the all the buttons
        for button in [self.lights_button, self.gps_button, 
                      self.camera_button, self.back_button]:
            button.setStyleSheet(button_style)


        self.lights_button.setStyleSheet(button_style)
        self.gps_button.setStyleSheet(button_style)
        self.camera_button.setStyleSheet(button_style)
        self.back_button.setStyleSheet(button_style)

        self.control_buttons_layout.addWidget(self.lights_button, 0, 0)
        self.control_buttons_layout.addWidget(self.gps_button, 0, 1)
        self.control_buttons_layout.addWidget(self.camera_button, 1, 0)
        self.control_buttons_layout.addWidget(self.back_button, 1, 1)

        self.vertical_layout.addWidget(self.control_buttons_frame)
    
    #function set container for the right panel
    def setup_right_panel(self):
        self.right_panel = QFrame()
        self.right_panel.setMinimumSize(341, 230)  # Set minimum size to 1/3 of the main window
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
    
    #implementation of timer used in date/time 
    def setup_datetime(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.update_datetime()

    #implementation of date/time function
    def update_datetime(self):
        current_datetime = QDateTime.currentDateTime()
        date_text = current_datetime.toString("dd-MM-yyyy")
        day_text = current_datetime.toString("dddd")
        self.date_label.setText(f"Date: {date_text}")
        self.day_label.setText(f"Day: {day_text}")

    #***************************************************************************#
    #implementation voice recogniyion
    #create object from VoiceThread
    #if command_detected has value or listening_status has value
    #jump to handle_voice_command function if command_detected true
    #jump to handle_voice_command function if listening_status true
    #***************************************************************************#

    def setup_voice_recognition(self):
        self.voice_thread = VoiceThread()
        self.voice_thread.command_detected.connect(self.handle_voice_command)
        self.voice_thread.listening_status.connect(self.update_mic_status)
        self.voice_thread.start()
    
    #***************************************************************************#
    #implementation control buttuns through voice
    #if command_detected (lights on-lights off-gps on-gps off- camera on-camera off)
    #jump to corosponding function(toggle_lights-toggle_gps-toggle_camera-back_to_main)
    #***************************************************************************#
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

    #function to update the mic color according to listening_status
    def update_mic_status(self, is_listening):
        self.mic_button.setStyleSheet(
            f"QPushButton#micButton {{ background-color: {'#ff9933' if is_listening else '#3498db'}; border-radius: 32px; }}"
        )


#***************************************************************************#
#implementation control buttuns through manual
#if button clicked 
#jump to corosponding function(toggle_lights-toggle_gps-toggle_camera-back_to_main)
#***************************************************************************#
    def connect_buttons(self):
        self.lights_button.clicked.connect(self.toggle_lights)
        self.gps_button.clicked.connect(self.toggle_gps)
        self.camera_button.clicked.connect(self.toggle_camera)
        self.back_button.clicked.connect(self.back_to_main)


#***************************************************************************#
#action after lights button clicked
#by defualt it "light on"
#if button clicked first time 
#
#jump to corosponding function(toggle_lights-toggle_gps-toggle_camera-back_to_main)
#***************************************************************************#
    def toggle_lights(self):
        self.lights_active = not self.lights_active
        self.lights_button.setText("Lights ON" if self.lights_active else "Lights OFF")
        self.lights_button.setDown(self.lights_active)  # This will trigger the :checked style
#***************************************************************************#
#action after gps button detected
#by defualt it "gps on"
#if button clicked first time 
#gps_active flag is true 
#jump to setup_google_maps function 
#***************************************************************************#
    def toggle_gps(self):
        self.gps_active = not self.gps_active
        self.gps_button.setText("GPS ON" if self.gps_active else "GPS OFF")
        self.gps_button.setDown(self.gps_active)  # This will trigger the :checked style

        if self.gps_active:
            self.setup_google_maps()
        else:
            if self.map_view:
                self.map_view.setParent(None)            #this remove the map from the parent widget
                self.map_view = None

#***************************************************************************#
#action after gps button clicked
#by defualt it is closed
#map_view flag is not None 
#open the window of the map
#***************************************************************************#
    def setup_google_maps(self):
        if not self.map_view:
            self.map_view = QWebEngineView()
            self.maps_layout.addWidget(self.map_view)
            self.map_view.setUrl(QUrl("https://www.google.com/maps"))


#***************************************************************************#
#action after camera button clicked
#by defualt it "camera on"
#if button clicked first time 
#camera_thread flag is true 
#jump to start_camera_feed function 
#***************************************************************************#
    def toggle_camera(self):
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_button.setText("Camera OFF")

            # Stop and clear camera feed
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None
            self.camera_label.clear()

            # Hide the camera panel
            self.camera_frame.setVisible(False)

            # Resize the right panel (map) to occupy more space
            self.right_panel.setMinimumSize((1024//2), 0)  # Adjust size as needed

        else:
            self.camera_button.setText("Camera ON")
            self.camera_button.setDown(True)  # This will trigger the :pressed style

            # Show the camera panel if hidden
            self.camera_frame.setVisible(True)

            # Restore the map panel size
            self.right_panel.setMinimumSize(300, 0)  # Restore to default size
            self.start_camera_feed()

#***************************************************************************#
#implementation camera thread
#create object from CameraThread
#if button clicked first time 
#camera_thread flag is true 
#jump to update_camera_feed function 
#***************************************************************************#
    def start_camera_feed(self):
        # Use 0 for webcam or video file path
        video_path = ("parking.mp4")
        # Get the camera label's dimensions
        camera_width = self.camera_label.width()
        camera_height = self.camera_label.height()
        self.camera_thread = CameraThread(video_path)
        #Initializes the camera thread with the video source
        self.camera_thread.frame_captured.connect(self.update_camera_feed)
        #Starts capture
        self.camera_thread.start()


    #function to update the camera frames r according to camera_label
    def update_camera_feed(self, qt_image):
        self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

#***************************************************************************#
#update the size of the of the camera frames
#***************************************************************************#
    #def resizeEvent(self, event):
    #    super().resizeEvent(event)
    #    if hasattr(self, 'camera_thread') and self.camera_thread:
            # Update detector dimensions   
    #        camera_width = self.camera_label.width()
    #        camera_height = self.camera_label.height()
    #        self.camera_thread.detector.display_width = camera_width
    #        self.camera_thread.detector.display_height = camera_height

#***************************************************************************#
#action after back button clicked
#clean ALL FLAGES
#jump to MainScreen screen
#***************************************************************************#
    def back_to_main(self):
        self.main_window = MainScreen.MainWindow()
        self.main_window.show()
        self.close()
#***************************************************************************#
#action to close all the threads 
#***************************************************************************#
    def closeEvent(self, event):
        if hasattr(self, "voice_thread") and self.voice_thread.isRunning():
            self.voice_thread.stop()
            self.voice_thread.wait()

        if hasattr(self, "camera_thread") and self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.quit()  # Stop the thread if it's running
            self.camera_thread.wait()  # Wait for it to finish

        event.accept()  # Ensures the window closes properly

#-----------------------------------------------------still need modification-----------------------------------//        

    #def toggle_keyboard(self):
    #    try:
    #        if not self.keyboard_process:
    #            if hasattr(self, 'search_input'):
    #                self.search_input.setFocus()
    #                self.search_input.raise_()
    #            
    #            # Calculate center position
    #            x_pos = (self.width() - 680) // 2
    #            y_pos = self.height() - 300 - 10
    #            
    #            # Launch xvkbd with additional options for input focus
    #            geometry = f"680x300+{x_pos}+{y_pos}"
    #            self.keyboard_process = subprocess.Popen([
    #                'xvkbd',
    #                '-geometry', geometry,
    #                '-compact',
    #                '-xsendevent',  # Use XSendEvent for key events
    #                '-secure',      # Enable secure mode
    #                '-no-jump-pointer',  # Don't move mouse pointer
    #                '-no-repeat'    # Disable key repeat
    #            ])
    #            
    #            # Set keyboard focus
    #            if hasattr(self, 'search_input'):
    #                self.search_input.activateWindow()
    #                self.search_input.setFocus(Qt.OtherFocusReason)
    #                
    #        else:
    #            self.keyboard_process.terminate()
    #            subprocess.run(['pkill', 'xvkbd'])
    #            self.keyboard_process = None
    #            
    #    except FileNotFoundError:
    #        try:
    #            # Install xvkbd if not found
    #            subprocess.run(['sudo', 'apt-get', 'update'])
    #            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'xvkbd'])
    #            
    #            if hasattr(self, 'search_input'):
    #                self.search_input.setFocus()
    #                self.search_input.raise_()
    #            geometry = f"680x300+{x_pos}+{y_pos}"
    #            self.keyboard_process = subprocess.Popen([
    #                'xvkbd',
    #                '-geometry', geometry,
    #                '-compact',
    #                '-xsendevent',
    #                '-secure',
    #                '-no-jump-pointer',
    #                '-no-repeat'
    #            ])
    #        except Exception as e:
    #            print(f"Error installing keyboard:", e)
#----------------------------------------------------------------------------------------//        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarWindow()
    window.show()
    sys.exit(app.exec_())