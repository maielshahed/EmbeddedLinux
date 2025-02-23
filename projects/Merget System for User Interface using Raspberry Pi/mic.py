#import speech_recognition as sr
#print(sr.Microphone.list_microphone_names())
from PyQt5.QtCore import QThread, pyqtSignal
import speech_recognition as sr

class VoiceThread(QThread):
    command_detected = pyqtSignal(str)
    listening_status = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self._running = True
        # Automatically select the webcam microphone
        mic_list = sr.Microphone.list_microphone_names()
        self.mic_index = None  # Default to None if not found

        for i, mic in enumerate(mic_list):
            if "WEB CAM" in mic:  # Match the name containing "WEB CAM"
                self.mic_index = i
                print (i)
                break  # Stop once we find the correct mic

    def run(self):
        if self.mic_index is None:
            print("Error: Webcam microphone not found!")
            return
        
        while self._running:
            try:
                with sr.Microphone(device_index=3) as source:
                    self.listening_status.emit(True)
                    audio = self.recognizer.listen(source)
                    text = self.recognizer.recognize_google(audio)
                    self.command_detected.emit(text.lower())
            except Exception as e:
                print(f"Error: {e}")

    def stop(self):
        self._running = False


voice_thread = VoiceThread()
voice_thread.start()