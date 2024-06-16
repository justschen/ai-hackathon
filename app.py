import os
import shutil
import subprocess
import sys
import threading
import time
import wave

import keyboard
import numpy as np
import pygame
import scipy.io.wavfile as wavfile
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
from pydub.playback import play
from pygame.locals import *
from PyQt5.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QLabel, QMenu,
                             QMenuBar, QPushButton, QToolBar, QVBoxLayout,
                             QWidget, QWidgetAction)
from rich import print
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from audio_player import AudioManager
from azure_speech_to_text import SpeechToTextManager
from eleven_labs import ElevenLabsManager
from obs_websockets import OBSWebsocketsManager
from openai_chat import OpenAiManager


def process_screenshot(app, screenshot_path):
    print(f"Processing screenshot: {screenshot_path}")
    app.handle_screenshot(screenshot_path)  # Call the method of MovingImageApp

class ScreenshotHandler(FileSystemEventHandler):
    
    def __init__(self, app):
        self.app = app
    
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(('.png', '.jpg', '.jpeg')):
            new_path = os.path.join(os.path.dirname(event.src_path), "SCREENSHOTDONOTREMOVE.png")
            os.rename(event.src_path, new_path)
            target_directory = os.path.expanduser('~/hackathon')
            os.makedirs(target_directory, exist_ok=True)
            target_path = os.path.join(target_directory, "SCREENSHOTDONOTREMOVE.png")
            shutil.move(new_path, target_path)
            print(f"Moved to: {target_path}")
            process_screenshot(self.app, target_path)
        else:
            print(f"File created but not a screenshot: {event.src_path}")


class TransparentLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = self.pixmap()
        if pixmap:
            painter.drawPixmap(self.rect(), pixmap)


class MovingImageApp(QWidget):
    def __init__(self):
        super().__init__()

        self.chunk = 1024
        self.paused = True
        self.stream = None
        self.amplitude = 0

        self.ELEVENLABS_VOICE = "fxEw0m0ujGLVPKYgEFCu" #Steven Voice

        self.BACKUP_FILE = "ChatHistoryBackup.txt"

        FIRST_SYSTEM_MESSAGE={"role": "system", "content": '''

        You are SteVen, a 32-year old Senior Software Engineering Manager that works at Microsoft. 
        You are very American and from Florida and have a passion for coding and building software. 
        DO NOT add any accents. 
        You are known for your expertise in all things Visual Studio Code (called VS Code). 
        You are MY manager.

        1) Provide short responses, about 1-2 paragraphs. 
        2) Always stay in character, no matter what. 
        3) Keep your answers limited to just a few sentences.
        4) When talking about code and code quality, be sure to be as blunt and rude and make sure to roast the author of said code.
        5) When talking about code, do NOT ever provide code snippets. Instead provide high level overviews and bullet points of what the code is doing or what can be fixed. 
        6) Frequently add remarks about how you are the best manager in the world.
        7) When I ask for help and a screenshot is provided, I want to know about the code in the image. Ignore everything that is not actual code. If there is no code in the image, say "I don't see any code in the image, and do your best to help me with the information you have as to what else is in the image. 
        8) If I ask for help and you don't know the answer, say "I don't know" and provide a funny anecdote about your time at Microsoft.
        9) DO NOT INCLUDE ASTERISKS IN YOUR RESPONSES.
        10) DO NOT EVER INCLUDE CODE SNIPPETS IN YOUR RESPONSES UNLESS PROVIDING HTML.
        11) If I ask for HTML, please provide all HTML and CSS in the response. 

        Okay, let the conversation begin!'''}

        FIRST_SYSTEM_MESSAGE={"role": "system", "content": '''
        Hi!'''}

        self.elevenlabs_manager = ElevenLabsManager()
        self.speechtotext_manager = SpeechToTextManager()
        self.openai_manager = OpenAiManager()
        self.audio_manager = AudioManager()

        self.openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Moving Image with Audio')
        screen_geometry = QApplication.desktop().screenGeometry()
        self.yPos = screen_geometry.bottom() - self.height()+40
        self.xPos = screen_geometry.left()
        self.setGeometry(screen_geometry.left(), self.yPos, self.width(), self.height())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

        layout = QVBoxLayout()

        # Create menu bar
        self.menu_bar = QMenuBar(self)
        self.menu = QMenu("Agents", self)
        self.menu_bar.addMenu(self.menu)

        # Add actions to the menu
        self.biden_action = QAction("SteVen", self)
        self.other_action = QAction("Kai", self)
        
        self.menu.addAction(self.biden_action)
        self.menu.addAction(self.other_action)

        self.biden_action.triggered.connect(lambda: self.change_image('steven.png'))
        self.other_action.triggered.connect(lambda: self.change_image('kai.png'))
        
        self.menu2 = QMenu("Actions", self)
        self.menu_bar.addMenu(self.menu2)

        # Add actions to the menu
        self.biden_action2 = QAction("Chat", self)
        self.other_action2 = QAction("Chat with Screenshot Context", self)
        
        self.menu2.addAction(self.biden_action2)
        self.menu2.addAction(self.other_action2)

        self.biden_action2.triggered.connect(lambda: self.chat())
        self.other_action2.triggered.connect(lambda: self.chatWithContext())
        
        layout.setMenuBar(self.menu_bar)

        self.label = QLabel(self)
        self.change_image('steven.png')  # Initial image load
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.show()
        # Create and start screenshot monitoring thread
        self.screenshot_path = get_screenshot_directory()
        if not os.path.exists(self.screenshot_path):
            print(f"Screenshot directory does not exist: {self.screenshot_path}")
            exit(1)

        self.event_handler = ScreenshotHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.screenshot_path, recursive=False)
        self.observer.start()

        print(f"Monitoring {self.screenshot_path} for screenshots...")

    def change_image(self, image_path):
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Adjust size here
        self.label.setPixmap(scaled_pixmap)
        if (image_path == 'steven.png'):
            self.ELEVENLABS_VOICE = "fxEw0m0ujGLVPKYgEFCu" # SteVen Voice ID
        else:
            self.ELEVENLABS_VOICE = "eu3Xpphwyn1T7Q07YAqB" # Kai Voice ID

    def chat(self):
        self.setupAI()

    def chatWithContext(self):
        self.setupAIContext()
    

    def setup_audio(self):
        pygame.mixer.music.load(self.audio_file)
        pygame.mixer.music.play()

    def update_image_position2(self):
        current_pos_ms = pygame.mixer.music.get_pos()  # Get current position in milliseconds
        if current_pos_ms < 0 or current_pos_ms >= self.duration * 1000:
            self.timer.stop()
            return
        
        self.current_time = current_pos_ms / 1000  # Convert to seconds
        current_index = int(self.current_time * self.samplerate)
        self.amplitude = self.wavform[current_index]
        x_offset = int((self.amplitude + 1) * (self.width() - self.label.width()) / 2)
        y_offset = int(0)

        self.label.move(x_offset*14-260, y_offset+20)

    def load_waveform(self):
        with wave.open(self.audio_file, 'rb') as wf:
            sample_rate, audio_data = wavfile.read(self.audio_file)

            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            normalized_samples = audio_data / np.max(np.abs(audio_data))
            # Apply exponential transformation for smoother and more pronounced waveform
            smooth_factor = 7.5  # Adjust this value to control the level of smoothing
            smoothed_samples = np.sign(normalized_samples) * (np.abs(normalized_samples) ** smooth_factor)

        return sample_rate, smoothed_samples

    def closeEvent(self, event):
        if self.stream:
            self.stream.stop()
      

    def handle_screenshot(self, screenshot_path):
        print(f"Screenshot taken: {screenshot_path}")
        self.setupAIContextPath(screenshot_path)


    def setupAI(self):

        mic_result = self.speechtotext_manager.speechtotext_from_mic_continuous()
            
        if mic_result == '':
            print("[red]Did not receive any input from your microphone!")

        openai_result = self.openai_manager.chat_with_history(mic_result)
        
        with open(self.BACKUP_FILE, "w") as file:
            file.write(str(self.openai_manager.chat_history))

        elevenlabs_output = self.elevenlabs_manager.text_to_audio(openai_result, self.ELEVENLABS_VOICE, False)

        self.audio_file = elevenlabs_output
        audio_data, sample_rate = sf.read(self.audio_file)
        sf.write('audiotoplayoutloud.wav', audio_data, sample_rate, subtype='PCM_16')
        self.audio_file = 'audiotoplayoutloud.wav'

        self.samplerate, self.wavform = self.load_waveform()
     
        self.duration = len(self.wavform) / self.samplerate
        self.current_time = 0
        self.timer_interval = 20  
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image_position2)
        self.timer.start(self.timer_interval)
        pygame.init()
        pygame.mixer.init()
        self.setup_audio()

        print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")


    def setupAIContext(self):

        mic_result = self.speechtotext_manager.speechtotext_from_mic_continuous()
            
        if mic_result == '':
            print("[red]Did not receive any input from your microphone!")

        openai_result = self.openai_manager.chat_with_screenshot(mic_result)
        
        with open(self.BACKUP_FILE, "w") as file:
            file.write(str(self.openai_manager.chat_history))

        elevenlabs_output = self.elevenlabs_manager.text_to_audio(openai_result, self.ELEVENLABS_VOICE, False)

        self.audio_file = elevenlabs_output
        audio_data, sample_rate = sf.read(self.audio_file)
        sf.write('audiotoplayoutloud.wav', audio_data, sample_rate, subtype='PCM_16')
        self.audio_file = 'audiotoplayoutloud.wav'
       
        self.samplerate, self.wavform = self.load_waveform()
      
        self.duration = len(self.wavform) / self.samplerate
        self.current_time = 0
        self.timer_interval = 20
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image_position2)
        self.timer.start(self.timer_interval)
        pygame.init()
        pygame.mixer.init()
        self.setup_audio()

        print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")


    def setupAIContextPath(self, screenshot_path):
        mic_result = self.speechtotext_manager.speechtotext_from_mic_continuous()
            
        if mic_result == '':
            print("[red]Did not receive any input from your microphone!")

        openai_result = self.openai_manager.chat_with_attachment(mic_result, screenshot_path)
        
        # with open(self.BACKUP_FILE, "w") as file:
        #     file.write(str(self.openai_manager.chat_history))

        elevenlabs_output = self.elevenlabs_manager.text_to_audio(openai_result, self.ELEVENLABS_VOICE, False)

        self.audio_file = elevenlabs_output
        audio_data, sample_rate = sf.read(self.audio_file)
        sf.write('audiotoplayoutloud.wav', audio_data, sample_rate, subtype='PCM_16')
        self.audio_file = 'audiotoplayoutloud.wav'
       
        self.samplerate, self.wavform = self.load_waveform()
      
        self.duration = len(self.wavform) / self.samplerate
        self.current_time = 0
        self.timer_interval = 20
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image_position2)
        self.timer.start(self.timer_interval)
        pygame.init()
        pygame.mixer.init()
        self.setup_audio()

        print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")


def get_screenshot_directory():
    try:
        result = subprocess.run(
            ["defaults", "read", "com.apple.screencapture", "location"],
            capture_output=True,
            text=True,
            check=True
        )
        path = result.stdout.strip()
        if not path:
            return os.path.expanduser("~/Desktop")
        return os.path.expanduser(path)  # Ensure the path is correctly expanded
    except Exception as e:
        print(f"Error finding screenshot directory: {e}")
        return os.path.expanduser("~/Desktop")
    

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MovingImageApp()
    # Start the GUI application
    sys.exit(app.exec_())




 