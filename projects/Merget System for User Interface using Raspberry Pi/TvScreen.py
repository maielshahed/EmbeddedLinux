import sys
import vlc
import yt_dlp
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
import MainScreen
# --------------------- Smart TV Window ---------------------
class TVWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)  # Remove window frame
        self.setGeometry(0, 0, 1042, 600)  # Set window size
        self.setStyleSheet("background-color: #001819;")  # Set background color

        # List of channels: (icon, YouTube link)
        self.channels = [
            ("aljazeera.png", "https://www.youtube.com/watch?v=bNyUyrR0PHo"),
            ("cartoon_network.png", "https://www.youtube.com/watch?v=zq8xgqZxb0k"),
            ("CBC_TV.png", ""),
            ("national.png", "https://www.youtube.com/watch?v=x5MkVTvOViQ"),
            ("CNC.png", ""),
            ("discovery.png", "")
        ]

        # Initialize VLC instance
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        # Create main widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Video display frame
        self.video_frame = QFrame(self)
        self.video_frame.setStyleSheet("background-color: black; border: 2px solid #7E9D9E;")
        self.video_frame.setFixedSize(1024, 450)  # Video frame size

        # Button layout
        button_layout = QHBoxLayout()
        for index, (icon, url) in enumerate(self.channels):
            button = self.create_button(icon, index)
            button_layout.addWidget(button)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_frame)
        layout.addLayout(button_layout)
        self.central_widget.setLayout(layout)

        # Back button (to go back to the main window)
        self.home_button = QPushButton(self)
        self.home_button.setIcon(QIcon("icons_back.png"))  # Set button icon
        self.home_button.setIconSize(QSize(100, 50))  # Set button size
        self.home_button.move(3, 570)  # Position button (x, y)
        self.home_button.clicked.connect(self.back_to_main)  # Connect to function

        # Link VLC to video frame
        if sys.platform.startswith("linux"):
            self.media_player.set_xwindow(int(self.video_frame.winId()))
        elif sys.platform == "win32":
            self.media_player.set_hwnd(int(self.video_frame.winId()))

    def create_button(self, icon_path, channel_index):
        """Create a channel button with an icon."""
        button = QPushButton(self)
        button.setFixedSize(100, 100)  # Set button size
        button.setIcon(QIcon(icon_path))  # Set button icon
        button.setIconSize(QSize(100, 100))  # Set icon size
        button.setStyleSheet("background-color: transparent; border: none; padding: 0px;")

        # Connect button to play video function
        button.clicked.connect(lambda: self.play_video(channel_index))
        return button

    def get_youtube_url(self, url):
        """Extract the direct video link from YouTube."""
        if not url:
            return None  # No video link available

        ydl_opts = {'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info['url']

    def play_video(self, channel_index):
        """Play the selected channel."""
        youtube_url = self.channels[channel_index][1]
        if not youtube_url:
            return  # No URL available for this channel

        direct_url = self.get_youtube_url(youtube_url)
        if not direct_url:
            return  # Failed to get a direct URL

        media = self.instance.media_new(direct_url)
        self.media_player.set_media(media)
        self.media_player.play()

    def close_stream(self):
        """Stop the video stream."""
        self.media_player.stop()

    def back_to_main(self):
        """Go back to the main window and stop the video."""
        self.close_stream()  # Stop the video before exiting
        self.main_window = MainScreen.MainWindow()
        self.main_window.show()
        self.close()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:  # If Escape is pressed
            self.close()  # Close the window
        elif event.key() == Qt.Key_Q:  # If Q is pressed
            self.close()  # Close the window
        else:
            super().keyPressEvent(event)  # Default behavior

# Running the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TVWindow()
    window.show()
    sys.exit(app.exec_())
