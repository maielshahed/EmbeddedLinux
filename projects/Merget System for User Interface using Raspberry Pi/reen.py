import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton,QVBoxLayout, QLabel 
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize,QUrl,QTimer


from PyQt5.QtMultimedia import QCamera, QCameraInfo

from PyQt5.QtWebEngineWidgets import QWebEngineView
import paho.mqtt.client as mqtt
from PyQt5.QtMultimediaWidgets import QVideoWidget
import cv2
import HomeScreen



class Camera:
    def __init__(self):
        self.video_label = QLabel()
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setAlignment(Qt.AlignCenter)
        
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.camera_button = QPushButton("Start Camera")
        self.camera_button.clicked.connect(self.toggle_camera)

    def toggle_camera(self):
        """ Start/Stop Camera on button press """
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.camera = None
                return
            self.timer.start(30)  # 30ms per frame
            self.camera_button.setText("Stop Camera")
        else:
            self.timer.stop()
            self.camera.release()
            self.camera = None
            self.video_label.clear()
            self.camera_button.setText("Start Camera")

    def update_frame(self):
        """ Capture and display camera frames """
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
            h, w, ch = frame.shape
            q_image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_image))



class MQTTClient:
    def __init__(self, broker, port, topic, username, password):
        self.broker = broker
        self.port = port
        self.topic = topic
        #self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client = mqtt.Client()
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

        #Back button home
        self.Home_button = self.create_toggle_button("Home", "icons_back.png", 20, 20)
        self.Home_button.clicked.connect(self.back_to_home)
        self.camera = Camera()  # This should be an instance of Camera, not a boolean
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
        self.timer = QTimer(self)  # Timer for updating frames


# زر تشغيل/إيقاف الكاميرا
        self.cameraButton = self.create_toggle_button("Camera", "camera.png", 20, 350)
        self.cameraButton.clicked.connect(self.camera.toggle_camera)

#----------------------------------------------RadioPlayer_button---------------------------------------------------------------
      
        self.playButton = self.create_toggle_button("Radio", "Play_Radio.png",20,130)
        self.playButton.clicked.connect(self.toggleRadio)

     
        # زر إخفاء المتصفح
        self.hideButton = self.create_toggle_button("Hide Radio", "Hide_Radio.png",20,240)
        self.hideButton.clicked.connect(self.hideRadio)
        self.hideButton.setEnabled(False)  # تعطيله في البداية حتى يبدأ التشغيل


                # إضافة المتصفح داخل النافذة مع تحديد حجمه ومكانه
         # متصفح مدمج (مخفي في البداية)
        self.browser = QWebEngineView()
        self.browser.hide()

    def toggleRadio(self):
        """تشغيل أو إيقاف الراديو عند الضغط على نفس الزر"""
        if self.playButton.isChecked():
            # تشغيل الراديو
            
            self.browser.setUrl(QUrl("https://surahquran.com/Radio-Quran-Cairo.html"))
            self.browser.show()
            self.hideButton.setEnabled(True) 
        else:
            # إيقاف الراديو
            self.browser.setUrl(QUrl())  # إيقاف التحميل
            self.browser.hide()


    def stopRadio(self):
        """إيقاف الراديو"""
        self.browser.setUrl(QUrl())  # إيقاف التحميل
        self.browser.hide()

        # إعادة تمكين زر التشغيل وتعطيل أزرار الإيقاف والإخفاء
        self.playButton.setEnabled(True)
        self.hideButton.setEnabled(False)
 
    def hideRadio(self):
        """إخفاء المتصفح بدون إيقاف الراديو"""
        self.browser.hide()
        self.hideButton.setEnabled(False)


#--------------------------------------------------------------------------------------------------------------


    def create_toggle_button(self, text, icon_path, x, y):
        """ إنشاء زر بتصميم Toggle """
        button = QPushButton(self)
        button.setGeometry(x, y, 90, 100)
        button.setCheckable(True)  # لجعل الزر قابل للتبديل
        button.setStyleSheet("""
            QPushButton {
                
                background-color: #1B3435;
                color: #34351B;
                text-align: center;
                border:none; 
                
            }
            
                             
            QPushButton:hover {
                background-color: #3A4F4F;  /* تأثير عند تمرير الماوس */
            }
            QPushButton:checked {
                color: #001819;
                background-color: #ED6C02;  /* تغيير لون الخلفية عند الضغط */       
                border: 2px solid #FFD700;  /* تغيير لون الإطار عند الضغط */

            }
 

        """)

        layout = QVBoxLayout()

        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(50, 50)))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")  # إزالة الخلفية الغامقة

        # **إنشاء النص**
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


    # الحدث لإغلاق النافذة عند الضغط على زر من الكيبورد
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # عند الضغط على زر Esc
            self.close()                 # إغلاق النافذة
        elif event.key() == Qt.Key_Q:    # عند الضغط على زر Q
            self.close()                 # إغلاق النافذة أيضًا
        else:
            super().keyPressEvent(event)  # تنفيذ الحدث الافتراضي


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoomWindow()
    window.show()
   
    sys.exit(app.exec_())




