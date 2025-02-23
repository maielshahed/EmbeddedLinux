


import sys


from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton,QWidget, QVBoxLayout, QLabel, QLCDNumber, QListWidget, QFileDialog, QSlider,QComboBox,QFrame,QHBoxLayout
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt, QSize



import HomeScreen
import TvScreen
import CarScreen






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
        self.sub_window = HomeScreen.HomeWindow()
        self.sub_window.show()
        self.close()

    def open_sub_window2(self):
        self.sub_window2 = TvScreen.TVWindow()
        self.sub_window2.show()
        self.close()

    def open_sub_window4(self):
         self.sub_window1 = CarScreen.CarWindow()
         self.sub_window1.show()
         self.close()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape: #ESC
            self.close()                 
        elif event.key() == Qt.Key_Q:    #Q
            self.close()                
        else:
            super().keyPressEvent(event)  





# --------------------- Run Application ---------------------
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
