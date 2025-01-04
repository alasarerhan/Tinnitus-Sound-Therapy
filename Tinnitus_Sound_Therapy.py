import sys
import numpy as np
import sounddevice as sd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QVBoxLayout, QWidget, QLabel, QSlider, QComboBox,
                           QHBoxLayout, QLineEdit)
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt
import random
from scipy import signal
import os

class FrequencyGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tinnitus Sound Therapy")
        self.setGeometry(100, 100, 400, 400)
        
        # Audio parameters
        self.sample_rate = 44100
        self.is_playing = False
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create sound type selector
        sound_label = QLabel("Sound Type:")
        self.sound_selector = QComboBox()
        self.sound_selector.addItems(["Gentle Rain", "Soft Wind", "Mixed Nature"])
        
        # Create frequency labels
        left_freq_layout = QHBoxLayout()
        left_freq_layout.addWidget(QLabel("Left ear frequency (Hz):"))
        self.left_freq_input = QLineEdit()
        self.left_freq_input.setText("4000")
        self.left_freq_input.setValidator(QDoubleValidator(20, 20000, 1))
        left_freq_layout.addWidget(self.left_freq_input)
        
        right_freq_layout = QHBoxLayout()
        right_freq_layout.addWidget(QLabel("Right ear frequency (Hz):"))
        self.right_freq_input = QLineEdit()
        self.right_freq_input.setText("4010")
        self.right_freq_input.setValidator(QDoubleValidator(20, 20000, 1))
        right_freq_layout.addWidget(self.right_freq_input)
        
        # Create volume sliders
        main_volume_label = QLabel("Main Volume:")
        self.main_volume_slider = QSlider(Qt.Horizontal)
        self.main_volume_slider.setMinimum(0)
        self.main_volume_slider.setMaximum(100)
        self.main_volume_slider.setValue(30)
        
        nature_volume_label = QLabel("Nature Sound Volume:")
        self.nature_volume_slider = QSlider(Qt.Horizontal)
        self.nature_volume_slider.setMinimum(0)
        self.nature_volume_slider.setMaximum(100)
        self.nature_volume_slider.setValue(50)
        
        # Create buttons
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_sound)
        
        # Add widgets to layout
        layout.addWidget(sound_label)
        layout.addWidget(self.sound_selector)
        layout.addLayout(left_freq_layout)
        layout.addLayout(right_freq_layout)
        layout.addWidget(main_volume_label)
        layout.addWidget(self.main_volume_slider)
        layout.addWidget(nature_volume_label)
        layout.addWidget(self.nature_volume_slider)
        layout.addWidget(self.play_button)
        
    def generate_filtered_noise(self, center_freq, bandwidth=100):
        noise = np.random.normal(0, 1, self.sample_rate)
        nyquist = self.sample_rate / 2
        low = (center_freq - bandwidth/2) / nyquist
        high = (center_freq + bandwidth/2) / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        filtered_noise = signal.filtfilt(b, a, noise)
        return filtered_noise / np.max(np.abs(filtered_noise))
    
    def generate_rain(self):
        # Generate rain sound (filtered noise with specific characteristics)
        noise = np.random.normal(0, 1, self.sample_rate)
        b, a = signal.butter(4, [1000/self.sample_rate*2, 4000/self.sample_rate*2], btype='band')
        rain = signal.filtfilt(b, a, noise)
        return rain / np.max(np.abs(rain))
    
    def generate_wind(self):
        # Generate wind sound (low-frequency filtered noise)
        noise = np.random.normal(0, 1, self.sample_rate)
        b, a = signal.butter(4, 500/self.sample_rate*2, btype='lowpass')
        wind = signal.filtfilt(b, a, noise)
        return wind / np.max(np.abs(wind))
    
    def audio_callback(self, outdata, frames, time, status):
        if self.is_playing:
            main_volume = self.main_volume_slider.value() / 100.0 * 0.3
            nature_volume = self.nature_volume_slider.value() / 100.0 * 0.7
            
            # Generate therapeutic noise
            left_noise = self.generate_filtered_noise(self.left_freq)
            right_noise = self.generate_filtered_noise(self.right_freq)
            
            # Generate nature sounds based on selection
            sound_type = self.sound_selector.currentText()
            if sound_type == "Gentle Rain":
                nature_sound = self.generate_rain()
            elif sound_type == "Soft Wind":
                nature_sound = self.generate_wind()
            else:  # Mixed Nature
                nature_sound = (self.generate_rain() * 0.5 + self.generate_wind() * 0.5)
            
            # Mix the sounds
            left_channel = (left_noise * main_volume + nature_sound * nature_volume)
            right_channel = (right_noise * main_volume + nature_sound * nature_volume)
            
            # Normalize to prevent clipping
            max_val = max(np.max(np.abs(left_channel)), np.max(np.abs(right_channel)))
            if max_val > 1.0:
                left_channel /= max_val
                right_channel /= max_val
            
            outdata[:frames, 0] = left_channel[:frames]
            outdata[:frames, 1] = right_channel[:frames]
        else:
            outdata.fill(0)
    
    def toggle_sound(self):
        if not self.is_playing:
            try:
                self.left_freq = float(self.left_freq_input.text())
                self.right_freq = float(self.right_freq_input.text())
                
                # Validate frequency range
                if not (20 <= self.left_freq <= 20000 and 20 <= self.right_freq <= 20000):
                    raise ValueError("Frequencies must be between 20 Hz and 20000 Hz")
                
                self.stream = sd.OutputStream(
                    channels=2,
                    samplerate=self.sample_rate,
                    callback=self.audio_callback
                )
                self.stream.start()
                self.is_playing = True
                self.play_button.setText("Stop")
            except ValueError as e:
                # You might want to add proper error handling here
                print(f"Invalid frequency value: {e}")
                return
        else:
            self.stream.stop()
            self.stream.close()
            self.is_playing = False
            self.play_button.setText("Play")

if __name__ == '__main__':
    print("Current working directory:", os.getcwd())
    app = QApplication(sys.argv)
    window = FrequencyGenerator()
    window.show()
    sys.exit(app.exec_())
