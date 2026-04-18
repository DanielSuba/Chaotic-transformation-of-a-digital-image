import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QComboBox, QLineEdit,
                             QLabel, QFileDialog, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import numpy as np

from script import ImageProcessor

class ImageScramblerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # script.py
        self.processor = ImageProcessor()

        # Nazwa programu + parametry okna
        self.setWindowTitle("Projekt M-II: Chaotyczne Przekształcanie Obrazu Cyfrowego")
        self.resize(1280, 800)
        self.setup_ui()

    # Konfiguracja interfeisu
    def setup_ui(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #2b2b2b; color: #ffffff; font-family: Arial; }
            QPushButton { background-color: #3c3f41; border: 1px solid #555555; padding: 6px 15px; border-radius: 4px; }
            QPushButton:hover { background-color: #505355; }
            QPushButton:pressed { background-color: #2c2e2f; }
            QLineEdit, QComboBox { background-color: #3c3f41; border: 1px solid #555555; padding: 5px; border-radius: 4px; }
            QGroupBox { border: 1px solid #555555; border-radius: 5px; margin-top: 10px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
            QLabel.image-label { background-color: #1e1e1e; border: 1px dashed #555555; }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # --------------- Górny panle Przycisków -------------------
        top_panel = QHBoxLayout()
        top_panel.setSpacing(10)

        self.btn_load = QPushButton("Wczytaj obraz")
        self.btn_load.clicked.connect(self.load_image)
        top_panel.addWidget(self.btn_load)

        self.combo_stage = QComboBox()
        self.combo_stage.addItems(["Etap 1: Naiwny", "Etap 2: Permutacja", "Etap 3: Wzmacniający"])
        top_panel.addWidget(self.combo_stage)

        self.btn_scramble = QPushButton("Scramble")
        self.btn_scramble.clicked.connect(self.scramble)
        top_panel.addWidget(self.btn_scramble)

        self.btn_unscramble = QPushButton("Unscramble")
        self.btn_unscramble.clicked.connect(self.unscramble)
        top_panel.addWidget(self.btn_unscramble)

        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("Wprowadź klucz...")
        top_panel.addWidget(self.input_key)

        self.btn_random_key = QPushButton("Random Key")
        self.btn_random_key.clicked.connect(self.random_key)
        top_panel.addWidget(self.btn_random_key)

        main_layout.addLayout(top_panel)

        # ---------------- Dolny panel dla obrazow ----------------
        images_layout = QHBoxLayout()

        self.lbl_original = self.create_image_gr("Oryginalny", images_layout)
        self.lbl_scrambled = self.create_image_gr("Przekształcony (Scrambled)", images_layout)
        self.lbl_recovered = self.create_image_gr("Odtworzony (Unscrambled)", images_layout)

        main_layout.addLayout(images_layout, stretch=1)

     # ---------------- Struktura obrazow ----------------
    def create_image_gr(self, title, parent_layout):
        group = QGroupBox(title)
        layout = QVBoxLayout()
        label = QLabel("Brak obrazu")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setProperty("class", "image-label")
        layout.addWidget(label)
        group.setLayout(layout)
        parent_layout.addWidget(group)
        return label

    # ---------------- Metody dla komunikacji ze skryptem ----------------
    # 1 obraz
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Wybierz obraz", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            if self.processor.load_image(file_name):
                self.display_image(self.processor.original_image, self.lbl_original)

    # 2 obraz
    def scramble(self):
        stage = self.combo_stage.currentIndex() + 1
        key = self.input_key.text()
        
        if not key:
            QMessageBox.warning(self, "Błąd", "Wprowadź klucz")
            return

    # 3 obraz
    def unscramble(self):
        stage = self.combo_stage.currentIndex() + 1
        key = self.input_key.text()
        
        if not key:
            QMessageBox.warning(self, "Błąd", "Wprowadź klucz")
            return

    def display_image(self, img_array, label):
        # Konwertuje tablicę NumPy na QPixmap
        if img_array is None:
            return

        height, width, channels = img_array.shape
        bytes_per_line = channels * width
        
        # Konwersja NumPy array (RGB) na QImage
        q_img = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Konwersja na QPixmap i skalowanie, aby obraz zachował proporcje
        pixmap = QPixmap.fromImage(q_img)
        
        # Pobieramy wymiary kontenera (etykiety)
        label_width = label.width()
        label_height = label.height()
        
        if label_width > 0 and label_height > 0:
            scaled_pixmap = pixmap.scaled(label_width, label_height, 
                                          Qt.AspectRatioMode.KeepAspectRatio, 
                                          Qt.TransformationMode.SmoothTransformation)
            label.setPixmap(scaled_pixmap)
        else:
            label.setPixmap(pixmap)
            
        label.setText("")
    
    # Random key
    def random_key(self):
        # Pobieramy losowy klucz z warstwy logiki
        stage = self.combo_stage.currentIndex() + 1
        new_key = self.processor.generate_random_key(stage)
        self.input_key.setText(new_key)

app = QApplication(sys.argv)
window = ImageScramblerGUI()
window.show()
sys.exit(app.exec())