import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLCDNumber, QComboBox, QPushButton, QSlider, QListWidget, QFileDialog, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QTime, QSize
from PyQt5.QtGui import QPalette, QColor, QFont, QPixmap, QIcon
import pygame.mixer
import requests
import RoomsScreen
import MainScreen
API_KEY = "9b461f6d62d59555b0471ff99ca0c782"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
# --------------------- Smart Home Window ---------------------
class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()



        
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(0, 0, 1024, 600)
        # self.setStyleSheet("background-color: #001819;")


      # Set background color
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#001819"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

      #digital clock display
        self.clock_display = QLCDNumber(self)
        self.clock_display.setGeometry(20, 20, 320, 120)
        self.clock_display.setStyleSheet("color: #7E9D9E; background: #1B3435; border: 2px solid #7E9D9E;")
        self.clock_display.setDigitCount(8)

        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()

        
        
                # **Add dropdown list to select city**
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

# Set the location and size of the QComboBox using setGeometry
        self.city_combo.setGeometry(20, 250, 420, 40)  # (x, y, width, height)

        # **🌤 Show weather**
        self.city_label = QLabel("Weather in Cairo", self)
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_label.setFont(QFont("Arial", 12))
        self.city_label.setStyleSheet("color: #7E9D9E;")
        self.city_label.setGeometry(70, 200, 350, 550)

        # Fixed area for weather display
        self.weather_display = QLabel(self)
        self.weather_display.setGeometry(20, 350, 390, 300)
        self.weather_display.setStyleSheet("""
            #background-color: #1B3435;
            border: 2px solid #7E9D9E;
            color: #FFD700;
        """)


      
        # Show weather icon
        self.weather_icon = QLabel(self.weather_display)
        self.weather_icon.setAlignment(Qt.AlignCenter)
        self.weather_icon.setFixedSize(150, 150)
        self.weather_icon.setStyleSheet("background: transparent;")

        # Temperature display
        self.result_label = QLabel("Fetching weather...", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.result_label.setStyleSheet("color: #FFD700;")
        self.result_label.setGeometry(20, 500, 300, 40)

        # Update weather on startup
        self.get_weather("Cairo")
        weather_timer = QTimer(self)
        weather_timer.timeout.connect(lambda: self.get_weather(self.city_combo.currentText()))
        weather_timer.start(1800000)  # Updated every 30 minutes




        # Setting up pygame to play audio
        pygame.mixer.init()
        self.is_playing = False
        self.is_repeating =False

        # Add MP3 files button
       
        self.add_button = self.create_toggle_button("Add", "icons_headphones.png", 900, 20)
        self.add_button.clicked.connect(self.add_mp3_to_playlist)

        # Music play/pause button
        self.play_button = self.create_toggle_button("Play", "icons_speaker.png", 900, 122)
        self.play_button.clicked.connect(self.toggle_play)

        # Music repeat button
        self.repeat_button = self.create_toggle_button("Repeat", "icons_repeat.png", 900, 224)
        self.repeat_button.clicked.connect(self.toggle_repeat)

      
        self.home_button = self.create_toggle_button("Home", "icons_house.png", 900, 326)
        self.home_button.clicked.connect(self.open_sub_window3)

        # Back to main window button

        self.back_button = self.create_toggle_button("Back", "icons_back.png", 900, 428)
        self.back_button.clicked.connect(self.back_to_main)


        # volume bar
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setGeometry(590, 320, 300, 30)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)

        # MP3 playlist
        self.playlist = QListWidget(self)
        self.playlist.setGeometry(590, 20, 300, 300)
        self.playlist.setStyleSheet("background-color: transparent; border: 1px solid #7E9D9E; color:#FFEE58;")



         # Set image as wallpaper
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(590, 20, 300, 300)
        self.bg_label.setPixmap(QPixmap("icons_music_note.jpg"))
        self.bg_label.setScaledContents(True)
        self.bg_label.lower()

        
        # pygame
        pygame.mixer.init()
        self.is_playing = False
        self.is_repeating = False
        self.current_track = None

        pygame.mixer.music.set_endevent(pygame.USEREVENT)  # Happened when the song ended
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_music_end)
        self.timer.start(1000)  # Check every second


    
    def create_toggle_button(self, text, icon_path, x, y):
        """ إنشاء زر بتصميم Toggle """
        button = QPushButton(self)
        button.setGeometry(x, y, 90, 100)
        button.setCheckable(True)  # To make the button toggleable
        button.setStyleSheet("""
            QPushButton {
                
                background-color: #1B3435;
                color: #1B3435;
                text-align: center;
                border:none;
                
            }
            
                             
            QPushButton:hover {
                background-color: #3A4F4F;  

            }
            QPushButton:checked {
                background-color: #ED6C02;  
                
                border: 2px solid #FFD700;  
            }
 

        """)
        layout = QVBoxLayout()
        
      
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(50, 50)))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")  

        # **Create text**
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
                # If no song is selected, we start from the first one.
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
        current_row = self.playlist.currentRow()  # Get current index
        if current_row < self.playlist.count() - 1:  # If we don't get to the last song
            next_row = current_row + 1
            self.playlist.setCurrentRow(next_row)  # Select next song
            track = self.playlist.item(next_row).text()
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            self.is_playing = True
            self.current_track = track
        else:
            # If we get to the last song, we stop.
            self.is_playing = False

    def check_music_end(self):
        if not pygame.mixer.music.get_busy() and self.is_playing:
            if self.is_repeating and self.current_track:
                # Replay the same song if repeat is enabled
                pygame.mixer.music.load(self.current_track)
                pygame.mixer.music.play()
            else:
                # Play next song
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
            # pixmap = QPixmap(f"http://openweathermap.org/img/wn/{icon_code}@2x.png")  #Use URL for icon
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
        self.main_window = MainScreen.MainWindow()
        self.main_window.show()
        self.close()

    def open_sub_window3(self):
        self.sub_window3 = RoomsScreen.RoomWindow()
        self.sub_window3.show()
        self.close()

 
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  
            self.close()                 
        elif event.key() == Qt.Key_Q:    
            self.close()                 
        else:
            super().keyPressEvent(event) 




# Running the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())
