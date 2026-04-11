import random
import numpy as np
from PIL import Image

class ImageProcessor:
    def __init__(self):
        self.image_path = None
        self.original_image = None
        self.scrambled_image = None
        self.unscrambled_image = None

    # Laduhe obraz
    def load_image(self, file_path):
        try:
            self.image_path = file_path
            # Konwetacja na format RGB)
            img = Image.open(file_path).convert('RGB')

            # Zamiana obrazu na tablicę NumPy
            self.original_image = np.array(img)
            
            print(f"Załadowano obraz o wymiarach: {self.original_image.shape}")
            return True
        except Exception as e:
            print(f"Błąd: {e}")
            return False

    # Random Key
    def generate_random_key(self):
        """Generuje losowy 16-znakowy klucz HEX."""
        return "".join(random.choices("0123456789ABCDEF", k=16))
    
    # Scramble
    def scramble(self, stage, key):
        if stage == 1:
            self.stage_1(key)
        elif stage == 2:
            self.stage_2(key)
        elif stage == 3:
            self.stage_3(key)
            
        return True #
    
    # UnScramble
    def unscramble(self, stage, key):
        return True

    # !!!!!!!!!!!!!!!!!!!! Etapy !!!!!!!!!!!!!!!!!!!!
    def stage_1(self, key):
        pass

    def stage_2(self, key):
        pass

    def stage_3(self, key):
        pass