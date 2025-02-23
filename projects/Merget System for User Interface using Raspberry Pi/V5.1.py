import sys
import vlc
import yt_dlp
import pygame
import requests
from PyQt5 import uic
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,QWidget, 
                            QVBoxLayout, QLabel, QLCDNumber, QListWidget, QFileDialog, 
                            QSlider,QComboBox,QFrame,QHBoxLayout,QGridLayout )

from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap, QFont,QDesktopServices

from PyQt5.QtCore import Qt, QTimer, QTime, QSize, QThread, pyqtSignal, QDateTime, QUrl,QIODevice
from PyQt5.QtWebEngineWidgets import QWebEngineView
import speech_recognition as sr

# تفاصيل API الطقس
API_KEY = "9b461f6d62d59555b0471ff99ca0c782"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"



# --------------------- Main Window ---------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Merget System for User Interface using Raspberry Pi.")
        self.setGeometry(0, 0, 1024, 600)
        self.setWindowIcon(QIcon("icons_home.png"))
        self.setStyleSheet("background-color: #1B3435;")


        #background colour configuration
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#001819"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        
        # Button to open Smart Home module
        self.cbc_button = QPushButton(self)
        self.cbc_button.setIcon(QIcon("iconsr_home.png"))
        self.cbc_button.setIconSize(QSize(250, 150))
        self.cbc_button.setGeometry(130, 200, 150, 150)
        self.cbc_button.setStyleSheet("background-color: transparent; border: none;")
        self.cbc_button.clicked.connect(self.open_sub_window)

        # Button to open Smart TV module
        self.cbc_buttontv = QPushButton(self)
        self.cbc_buttontv.setIcon(QIcon("icons_tv.png"))
        self.cbc_buttontv.setIconSize(QSize(150, 150))
        self.cbc_buttontv.setGeometry(440, 200, 150, 150)
        self.cbc_buttontv.setStyleSheet("background-color: transparent; border: none;")
        self.cbc_buttontv.clicked.connect(self.open_sub_window2)


        # Button to open infotianment system in car module
        self.cbc_button_car = QPushButton(self)
        self.cbc_button_car.setIcon(QIcon("car.png"))
        self.cbc_button_car.setIconSize(QSize(150, 150))
        self.cbc_button_car.setGeometry(764, 200, 150, 150)
        self.cbc_button_car.setStyleSheet("background-color: transparent; border: none;")
        self.cbc_button_car.clicked.connect(self.open_sub_window4)

        # Add logo at the bottom middle
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap("LOGO.png").scaled(120, 120, Qt.KeepAspectRatio))  # Replace "logo.png" with your logo file
        self.logo_label.setGeometry((1024 - 130) // 2, 600 - 130, 120, 120)  # Position at bottom middle
        self.logo_label.setStyleSheet("background-color: transparent;")


    def open_sub_window(self):
        self.sub_window = SubWindow()
        self.sub_window.show()
        self.close()

    def open_sub_window2(self):
        self.sub_window2 = TVWindow()
        self.sub_window2.show()
        self.close()

    def open_sub_window4(self):
        self.sub_window4 = SmartControlHub()
        self.sub_window4.show()
        self.close()


    # الحدث لإغلاق النافذة عند الضغط على زر من الكيبورد
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # عند الضغط على زر Esc
            self.close()                 # إغلاق النافذة
        elif event.key() == Qt.Key_Q:    # عند الضغط على زر Q
            self.close()                 # إغلاق النافذة أيضًا
        else:
            super().keyPressEvent(event)  # تنفيذ الحدث الافتراضي


# --------------------- Smart Home Window ---------------------
class SubWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(0, 0, 1024, 600)
        # self.setStyleSheet("background-color: #001819;")


        # تعيين لون الخلفية
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#001819"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # شاشة عرض الساعة الرقمية
        self.clock_display = QLCDNumber(self)
        self.clock_display.setGeometry(20, 20, 320, 120)
        self.clock_display.setStyleSheet("color: #7E9D9E; background: #1B3435; border: 2px solid #7E9D9E;")
        self.clock_display.setDigitCount(8)

        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()

        
        
                # **إضافة قائمة منسدلة لاختيار المدينة**
        self.city_combo = QComboBox(self)
        self.city_combo.addItem("Cairo")
        self.city_combo.addItem("German")
        self.city_combo.addItem("Saudi Arabia")
        self.city_combo.addItem("New York")
        self.city_combo.addItem("London")
        self.city_combo.addItem("Tokyo")
        self.city_combo.addItem("Paris")
        self.city_combo.setStyleSheet("""
            background-color: #1B3435;
            color: #7E9D9E;
            font-size: 18px;
            border-radius: 5px;
            padding: 5px;
        """)
        self.city_combo.currentIndexChanged.connect(self.on_city_selected)

        # تحديد مكان وحجم QComboBox باستخدام setGeometry
        self.city_combo.setGeometry(20, 250, 420, 40)  # (x, y, العرض, الارتفاع)

        # **🌤 عرض الطقس**
        self.city_label = QLabel("Weather in Cairo", self)
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_label.setFont(QFont("Arial", 12))
        self.city_label.setStyleSheet("color: #7E9D9E;")
        self.city_label.setGeometry(70, 200, 350, 550)

        # مساحة ثابتة لعرض الطقس
        self.weather_display = QLabel(self)
        self.weather_display.setGeometry(20, 350, 390, 300)
        self.weather_display.setStyleSheet("""
            #background-color: #1B3435;
            border: 2px solid #7E9D9E;
            color: #FFD700;
        """)

        # عرض أيقونة الطقس
        self.weather_icon = QLabel(self.weather_display)
        self.weather_icon.setAlignment(Qt.AlignCenter)
        self.weather_icon.setFixedSize(150, 150)
        self.weather_icon.setStyleSheet("background: transparent;")

        # عرض درجة الحرارة
        self.result_label = QLabel("Fetching weather...", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.result_label.setStyleSheet("color: #FFD700;")
        self.result_label.setGeometry(20, 500, 300, 40)

        # تحديث الطقس عند بدء التشغيل
        self.get_weather("Cairo")
        weather_timer = QTimer(self)
        weather_timer.timeout.connect(lambda: self.get_weather(self.city_combo.currentText()))
        weather_timer.start(1800000)  # تحديث كل 30 دقيقة




        # إعداد pygame لتشغيل الصوتيات
        pygame.mixer.init()
        self.is_playing = False
        self.is_repeating =False

        # زر إضافة ملفات MP3
       
        self.add_button = self.create_toggle_button("Add", "icons_headphones.png", 900, 20)
        self.add_button.clicked.connect(self.add_mp3_to_playlist)

        # زر تشغيل/إيقاف الموسيقى
        self.play_button = self.create_toggle_button("Play", "icons_speaker.png", 900, 122)
        self.play_button.clicked.connect(self.toggle_play)

        # زر تكرار الموسيقى
        self.repeat_button = self.create_toggle_button("Repeat", "icons_repeat.png", 900, 224)
        self.repeat_button.clicked.connect(self.toggle_repeat)

      
        self.home_button = self.create_toggle_button("Home", "icons_house.png", 900, 326)
        self.home_button.clicked.connect(self.open_sub_window3)

        # زر العودة إلى النافذة الرئيسية

        self.back_button = self.create_toggle_button("Back", "icons_back.png", 900, 428)
        self.back_button.clicked.connect(self.back_to_main)


        # شريط مستوى الصوت
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setGeometry(590, 320, 300, 30)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)

        # قائمة تشغيل MP3
        self.playlist = QListWidget(self)
        self.playlist.setGeometry(590, 20, 300, 300)
        self.playlist.setStyleSheet("background-color: transparent; border: 1px solid #7E9D9E; color:#FFEE58;")



         # تعيين صورة كخلفية
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(590, 20, 300, 300)
        self.bg_label.setPixmap(QPixmap("icons_music_note.jpg"))
        self.bg_label.setScaledContents(True)
        self.bg_label.lower()

        
        # إعداد pygame
        pygame.mixer.init()
        self.is_playing = False
        self.is_repeating = False
        self.current_track = None

        pygame.mixer.music.set_endevent(pygame.USEREVENT)  # حدث عند انتهاء الأغنية
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_music_end)
        self.timer.start(1000)  # فحص كل ثانية


    
    def create_toggle_button(self, text, icon_path, x, y):
        """ إنشاء زر بتصميم Toggle """
        button = QPushButton(self)
        button.setGeometry(x, y, 90, 100)
        button.setCheckable(True)  # لجعل الزر قابل للتبديل
        button.setStyleSheet("""
            QPushButton {
                
                background-color: #1B3435;
                color: #1B3435;
                text-align: center;
                border:none;
                
            }
            
                             
            QPushButton:hover {
                background-color: #3A4F4F;  /* تأثير عند تمرير الماوس */

            }
            QPushButton:checked {
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


  
        button.setLayout(layout)

        return button



    def update_clock(self):
        current_time = QTime.currentTime().toString('HH:mm:ss')
        self.clock_display.display(current_time)

    def add_mp3_to_playlist(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select MP3 Files", "", "MP3 Files (*.mp3)")
        for file in files:
            self.playlist.addItem(file)

    

    def toggle_play(self):
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.play_button.setText(" ")
        else:
            if self.playlist.selectedItems():
                track = self.playlist.selectedItems()[0].text()
            else:
                # إذا لم يتم تحديد أغنية، نبدأ من الأولى
                self.playlist.setCurrentRow(0)
                track = self.playlist.item(0).text()

            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            self.is_playing = True
            self.current_track = track
            self.play_button.setText(" ")

    # def toggle_repeat(self):
    #     self.is_repeating = not self.is_repeating

    def toggle_repeat(self):
        self.is_repeating = not self.is_repeating

    def play_next_song(self):
        current_row = self.playlist.currentRow()  # الحصول على الفهرس الحالي
        if current_row < self.playlist.count() - 1:  # إذا لم نصل إلى آخر أغنية
            next_row = current_row + 1
            self.playlist.setCurrentRow(next_row)  # تحديد الأغنية التالية
            track = self.playlist.item(next_row).text()
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            self.is_playing = True
            self.current_track = track
        else:
            # إذا وصلنا إلى آخر أغنية، نتوقف
            self.is_playing = False

    def check_music_end(self):
        if not pygame.mixer.music.get_busy() and self.is_playing:
            if self.is_repeating and self.current_track:
                # إعادة تشغيل نفس الأغنية إذا كان التكرار مفعّلًا
                pygame.mixer.music.load(self.current_track)
                pygame.mixer.music.play()
            else:
                # تشغيل الأغنية التالية
                self.play_next_song()

    def change_volume(self):
        volume = self.volume_slider.value() / 100
        pygame.mixer.music.set_volume(volume)


    
    def on_city_selected(self):
        """Update weather when selecting a new city"""
        selected_city = self.city_combo.currentText()
        self.get_weather(selected_city)

    def get_weather(self, city_name):
        """Get and display weather data"""
        params = {"q": city_name, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            weather = data["weather"][0]["description"]
            icon_code = data["weather"][0]["icon"]

            # # url cloud
            # pixmap = QPixmap(f"http://openweathermap.org/img/wn/{icon_code}@2x.png")  # استخدم URL للأيقونة
            # self.weather_icon.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))

            pixmap = QPixmap("cloudy.png")  # Put image path here
            self.weather_icon.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))

            # تحديث النصوص
            self.city_label.setText(f"Weather in {city_name}")
            self.result_label.setText(f"🌡 {temp}°C | {weather.capitalize()}")
        else:
            self.result_label.setText("❌ Failed to fetch weather.")




   
#Exit page and go home page
    def back_to_main(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

    def open_sub_window3(self):
        self.sub_window3 = SubWindow3()
        self.sub_window3.show()
        self.close()

    # الحدث لإغلاق النافذة عند الضغط على زر من الكيبورد
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # عند الضغط على زر Esc
            self.close()                 # إغلاق النافذة
        elif event.key() == Qt.Key_Q:    # عند الضغط على زر Q
            self.close()                 # إغلاق النافذة أيضًا
        else:
            super().keyPressEvent(event)  # تنفيذ الحدث الافتراضي



# --------------------- room home ---------------------
class SubWindow3(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(0, 0, 1024, 600)
        self.setStyleSheet("background-color: #001819;")

        #Back button home
        self.Home_button = self.create_toggle_button("Home", "icons_back.png", 20, 20)
        self.Home_button.clicked.connect(self.back_to_home)
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

    

    def create_toggle_button(self, text, icon_path, x, y):
        """ إنشاء زر بتصميم Toggle """
        button = QPushButton(self)
        button.setGeometry(x, y, 90, 100)
        button.setCheckable(True)  # لجعل الزر قابل للتبديل
        button.setStyleSheet("""
            QPushButton {
                
                background-color: #1B3435;
                color: #1B3435;
                text-align: center;
                border:none;
                
            }
            
            QPushButton:hover {
                background-color: #3A4F4F;  /* تأثير عند تمرير الماوس */

            }
            QPushButton:checked {
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

        button.setLayout(layout)

        return button



  #-------------------------------------------------------------

   
#Back button home
    def back_to_home(self):
        self.main_window = SubWindow()
        self.main_window.show()
        self.close()


    # الحدث لإغلاق النافذة عند الضغط على زر من الكيبورد
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # عند الضغط على زر Esc
            self.close()                 # إغلاق النافذة
        elif event.key() == Qt.Key_Q:    # عند الضغط على زر Q
            self.close()                 # إغلاق النافذة أيضًا
        else:
            super().keyPressEvent(event)  # تنفيذ الحدث الافتراضي






#--------------------- Smart TV Window ---------------------
class TVWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(0, 0, 1042, 600)
        self.setStyleSheet("background-color: #001819;")

        # قائمة القنوات: (الصورة, رابط YouTube, موضع الزر)
        self.channels = [
            ("aljazeera.png", "https://www.youtube.com/watch?v=bNyUyrR0PHo"),
            ("cartoon_network.png", "https://www.youtube.com/watch?v=zq8xgqZxb0k"),
            ("CBC_TV.png", ""),
            ("national.png", "https://www.youtube.com/watch?v=x5MkVTvOViQ"),
            ("CNC.png", ""),
            ("discovery.png", "")   
        ]

        # VLC instance
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        # Main widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)



        # إطار عرض الفيديو
        self.video_frame = QFrame(self)
        self.video_frame.setStyleSheet("background-color: black; border: 2px solid #7E9D9E;")
        self.video_frame.setFixedSize(1024, 450)  # حجم الفيديو
       
        # تخطيط الأزرار
        button_layout = QHBoxLayout()
        for index, (icon, url) in enumerate(self.channels):
            button = self.create_button(icon, index)
            button_layout.addWidget(button)

        # التخطيط الرئيسي
        layout = QVBoxLayout()
        layout.addWidget(self.video_frame)
        layout.addLayout(button_layout)
        self.central_widget.setLayout(layout)

              #Back button home
        self.home_button = QPushButton(self)
        self.home_button.setIcon(QIcon("icons_back.png"))  # icon
        self.home_button.setIconSize(QSize(100, 50))  #ةsize
        self.home_button.move(3, 570)  # 🔥x,y
        self.home_button.clicked.connect(self.back_to_main)

        # ربط VLC بإطار الفيديو
        if sys.platform.startswith("linux"):
            self.media_player.set_xwindow(int(self.video_frame.winId()))
        elif sys.platform == "win32":
            self.media_player.set_hwnd(int(self.video_frame.winId()))

    def create_button(self, icon_path, channel_index):
        """دالة لإنشاء زر قناة مع الصورة"""
        button = QPushButton(self)
        button.setFixedSize(100, 100)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(100, 100))
        button.setStyleSheet("background-color: transparent; border: none; padding: 0px;")
        
        # ربط الزر بتشغيل القناة
        button.clicked.connect(lambda: self.play_video(channel_index))
        return button

    def get_youtube_url(self, url):
        """استخراج رابط الفيديو المباشر من YouTube"""
        if not url:
            return None  # لا يوجد فيديو لهذه القناة
        ydl_opts = {'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info['url']

    def play_video(self, channel_index):
        """تشغيل القناة المحددة"""
        youtube_url = self.channels[channel_index][1]
        if not youtube_url:
            return  # لا يوجد رابط للقناة
        
        direct_url = self.get_youtube_url(youtube_url)
        if not direct_url:
            return  # فشل جلب الرابط
        
        media = self.instance.media_new(direct_url)
        self.media_player.set_media(media)
        self.media_player.play()

    def close_app(self):
        """close video """
        self.media_player.stop()
        self.close()

        
    def back_to_main(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  #click Esc
            self.close()                 # close window
        elif event.key() == Qt.Key_Q:    # click Q
            self.close()                 # close windo
        else:
            super().keyPressEvent(event)  

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

class SmartControlHub(QMainWindow):
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
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

    def closeEvent(self, event):
        self.voice_thread.stop()
        self.voice_thread.wait()
        self.timer.stop()
        event.accept()


# --------------------- Run Application ---------------------
def main():

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
