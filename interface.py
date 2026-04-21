import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QComboBox, QLineEdit,
                             QLabel, QFileDialog, QGroupBox, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import numpy as np

# script.py
from script import ImageProcessor
# interfaceINFO.py
from interfaceINFO import InfoWindow

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

        self.btn_load = QPushButton("Upload image")
        self.btn_load.clicked.connect(self.load_image)
        top_panel.addWidget(self.btn_load)

        self.btn_download = QPushButton("Download image")
        self.btn_download.clicked.connect(self.download_image)
        top_panel.addWidget(self.btn_download)

        self.btn_info = QPushButton("Show information")
        self.btn_info.clicked.connect(self.show_information)
        top_panel.addWidget(self.btn_info)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset_ui)
        top_panel.addWidget(self.btn_reset)

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
        self.input_key.setPlaceholderText("Write key...")
        top_panel.addWidget(self.input_key)

        self.btn_random_key = QPushButton("Random Key")
        self.btn_random_key.clicked.connect(self.random_key)
        top_panel.addWidget(self.btn_random_key)

        main_layout.addLayout(top_panel)

        # ---------------- Dolny panel dla obrazow ----------------
        images_layout = QHBoxLayout()

        self.lbl_original = self.create_image_gr("Original", images_layout)
        self.lbl_scrambled = self.create_image_gr("Scrambled", images_layout)
        self.lbl_recovered = self.create_image_gr("Unscrambled", images_layout)

        main_layout.addLayout(images_layout, stretch=1)

     # ---------------- Struktura obrazow ----------------
    def create_image_gr(self, title, parent_layout):
        group = QGroupBox(title)
        layout = QVBoxLayout()
        label = QLabel("Imageless")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setProperty("class", "image-label")
        layout.addWidget(label)
        group.setLayout(layout)
        parent_layout.addWidget(group)
        return label

    # ---------------- Metody dla komunikacji ze skryptem ----------------
    # 1 obraz
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            if self.processor.load_image(file_name):
                self.display_image(self.processor.original_image, self.lbl_original)

    # 2 obraz
    def scramble(self):
        stage = self.combo_stage.currentIndex() + 1
        key = self.input_key.text()
        
        if not key:
            QMessageBox.warning(self, "Error", "Write key")
            return
        
        if self.processor.original_image is None:
            QMessageBox.warning(self, "Error", "Upload image first!")
            return

        if self.processor.scramble(stage, key):
            self.display_image(self.processor.scrambled_image, self.lbl_scrambled)
        else:
            QMessageBox.critical(self, "Error", "Check key format!")

    # 3 obraz
    def unscramble(self):
        stage = self.combo_stage.currentIndex() + 1
        key = self.input_key.text()
        
        if not key:
            QMessageBox.warning(self, "Error", "Write key")
            return
        
        options = []
        if self.processor.original_image is not None:
            options.append("Original Image")
        if self.processor.scrambled_image is not None:
            options.append("Scrambled Image")

        if not options:
            QMessageBox.warning(self, "Error", "No image to unscramble!")
            return

        # Jesli sa oba, to mozno wybrac
        if len(options) == 2:
            choice, ok = QInputDialog.getItem(self, "Unscramble Source", "Which image do you want to unscramble?", options, 0, False)
            if not ok:
                return
        else:
            choice = options[0]

        source_param = "original" if choice == "Original Image" else "scrambled"

        if self.processor.unscramble(stage, key, source=source_param):
            self.display_image(self.processor.unscrambled_image, self.lbl_recovered)
        else:
            QMessageBox.critical(self, "Error", "Not original key or wrong format!")

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
    
    # Zapis obrazu
    def download_image(self):
        # Sprawdzamy, jakie obrazy są dostępne do zapisu
        options = []
        if self.processor.scrambled_image is not None:
            options.append("Scrambled Image")
        if self.processor.unscrambled_image is not None:
            options.append("Unscrambled Image")

        if not options:
            QMessageBox.warning(self, "Error", "No image available to download!")
            return

        # Jeśli są oba, bedzie dany wybór
        if len(options) == 2:
            choice, ok = QInputDialog.getItem(self, "Download Image", "Which image do you want to save?", options, 0, False)
            if not ok:
                return
        else:
            choice = options[0]

        # Wybór ścieżki i nazwy pliku
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png)")
        
        if file_path:
            # Ustalenie, która tablica NumPy ma zostać zapisana
            img_array = self.processor.scrambled_image if choice == "Scrambled Image" else self.processor.unscrambled_image
            
            # Konwersja NumPy na QImage i zapisanie
            height, width, channels = img_array.shape
            bytes_per_line = channels * width
            q_img = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            
            if q_img.save(file_path, "PNG"):
                QMessageBox.information(self, "Success", f"{choice} saved successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to save the image.")
    
    # Resetowanie programu
    def reset_ui(self):
        # Czyści obrazy w interfejsie
        self.lbl_original.clear()
        self.lbl_original.setText("Imageless")
        self.lbl_scrambled.clear()
        self.lbl_scrambled.setText("Imageless")
        self.lbl_recovered.clear()
        self.lbl_recovered.setText("Imageless")
        
        self.input_key.clear()
        
        # Czyszczenie danych w skrypcie
        self.processor.original_image = None
        self.processor.scrambled_image = None
        self.processor.unscrambled_image = None
        print("Reset acquired")
    
    # Informacja
    def show_information(self):
        stage = self.combo_stage.currentIndex() + 1
        key = self.input_key.text()
        
        # Tworzymy instancję nowego okna i przekazujemy nasze dane
        # self jako parent sprawia, że nowe okno wyśrodkuje się na głównym oknie
        self.info_window = InfoWindow(self.processor, stage, key, parent=self)
        self.info_window.exec() # .exec() blokuje okno główne

    # Random key
    def random_key(self):
        # Pobieramy losowy klucz z warstwy logiki i etapu
        stage = self.combo_stage.currentIndex() + 1
        new_key = self.processor.generate_random_key(stage)
        self.input_key.setText(new_key)

app = QApplication(sys.argv)
window = ImageScramblerGUI()
window.show()
sys.exit(app.exec())