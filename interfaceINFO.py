from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog, QMessageBox
# scriptINFO.py
from scriptINFO import ImageAnalyzer

class InfoWindow(QDialog):
    def __init__(self, processor, stage, key, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Information")
        self.resize(650, 600)
        
        # Styl
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: #ffffff; font-family: Arial; }
            QTextEdit { background-color: #1e1e1e; color: #00ffcc; border: 1px solid #555555; padding: 10px; font-family: Consolas, monospace; font-size: 13px;}
            QPushButton { background-color: #3c3f41; color: white; border: 1px solid #555555; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #505355; }
        """)

        layout = QVBoxLayout(self)

        # Pole tekstowe
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # Panel przycisków na dole
        buttons_layout = QHBoxLayout()

        self.btn_save = QPushButton("Save as .txt")
        self.btn_save.clicked.connect(self.save_to_txt)
        buttons_layout.addWidget(self.btn_save)

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_close)

        layout.addLayout(buttons_layout)

        # Wygeneruj raport
        self.generate_report(processor, stage, key)

    def save_to_txt(self):
        # Pobiera tekst z logu i zapisuje do pliku .txt
        content = self.log_area.toPlainText()
        if not content:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save report", "Information.txt", "Text Files (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", f"Report has been saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{str(e)}")

    def generate_report(self, proc, stage, key):
        log = []
        log.append(f"=== ANALYSIS: STAGE {stage} ===")
        log.append(f"Key: {key if key else 'None'}\n")
        
        # ORIGINAL -> SCRAMBLE
        if proc.original_image is not None and proc.scrambled_image is not None:
            log.append("--- Original -> Scrambled ---")
            sim = ImageAnalyzer.similarity(proc.original_image, proc.scrambled_image)
            log.append(f"Similarity: {sim:.2f}%")
            
            corr_orig = ImageAnalyzer.correlation(proc.original_image)
            corr_scr = ImageAnalyzer.correlation(proc.scrambled_image)
            log.append(f"Original correlation: {corr_orig:.4f}")
            log.append(f"Scrambled correlation: {corr_scr:.4f}")

            if key:
                fake_key = "+R999" if stage == 1 else "WRONG_KEY_123"
                old_unscrambled = proc.unscrambled_image 
                
                proc.unscramble(stage, fake_key, source="scrambled")
                bad_result = proc.unscrambled_image
                
                diff = ImageAnalyzer.similarity(proc.original_image, bad_result)
                log.append(f"Similarity when using wrong key: {diff:.2f}%\n")
                
                proc.unscrambled_image = old_unscrambled
        
        # Scrambled -> Unscrambled
        if proc.scrambled_image is not None and proc.unscrambled_image is not None:
            log.append("--- Scrambled -> Unscrambled ---")
            sim = ImageAnalyzer.similarity(proc.scrambled_image, proc.unscrambled_image)
            log.append(f"Similarity (Scrambled vs Recovered): {sim:.2f}%\n")
        
        # Original -> Unscrambled
        if proc.original_image is not None and proc.unscrambled_image is not None:
            log.append("--- Original -> Unscrambled (REVERSIBILITY TEST) ---")
            sim = ImageAnalyzer.similarity(proc.original_image, proc.unscrambled_image)
            if sim == 100.0:
                log.append(f"STATUS: SUCCESS! Algorithm is 100% reversible. Similarity: {sim:.2f}%\n")
            else:
                log.append(f"STATUS: ERROR! Image was not fully recovered. Similarity: {sim:.2f}%\n")

        # Metryki kolorow
        log.append("=== COLOR METRICS (TOP 5) ===")
        if proc.original_image is not None:
            log.append("\n[Original]")
            for color, count in ImageAnalyzer.top_5(proc.original_image):
                log.append(f"  RGB {color}: {count} pixels")
                
        if proc.scrambled_image is not None:
            log.append("\n[Scrambled]")
            for color, count in ImageAnalyzer.top_5(proc.scrambled_image):
                log.append(f"  RGB {color}: {count} pixels")
                
        if proc.unscrambled_image is not None:
            log.append("\n[Unscrambled]")
            for color, count in ImageAnalyzer.top_5(proc.unscrambled_image):
                log.append(f"  RGB {color}: {count} pixels")

        self.log_area.setPlainText("\n".join(log))