import random
import numpy as np
from PIL import Image
import re

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
    def generate_random_key(self, stage):
        if stage == 1:
            # Losuje +, - oraz C, R i przesunięcie od 10 do 300 pikseli
            sign = random.choice(['+', '-'])
            axis = random.choice(['R', 'C'])
            shift = random.randint(10, 300)
            return f"{sign}{axis}{shift}"
        else:
            # Generuje losowy 16-znakowy klucz HEX
            return "".join(random.choices("0123456789ABCDEF", k=16))
    
    # Metoda sprawdzenia i do rozkodowania Etapu 1
    def stage1_key(self, key):
        # Sprawdza czy format jest prawidlowy
        match = re.match(r'^([+-])([RCrc])(\d+)$', key.strip())
        if not match:
            raise ValueError("Zły format klucza! Użyj np. +R50 lub -C100")
        
        sign = 1 if match.group(1) == '+' else -1
        # Jezeli R to wiersze przemieszczają się w po X kord
        # Jezeli C to kolumny przemieszczają się w po Y kord
        axis = 1 if match.group(2).upper() == 'R' else 0
        shift = int(match.group(3)) * sign

        return axis, shift

    # Scramble
    def scramble(self, stage, key):
        # Jezeli niema obrazu
        if self.original_image is None:
            return False

        # Sprawdzenie
        try:
            if stage == 1:
                self.stage_1(key)
            elif stage == 2:
                self.stage_2(key)
            elif stage == 3:
                self.stage_3(key)
            return True
        except Exception as e:
            print(f"Blad szyfrowania: {e}")
            return False
    
    # UnScramble
    def unscramble(self, stage, key):
        if self.scrambled_image is None:
            return False
            
        try:
            if stage == 1:        # Unscramble dla etapu 1 w odwrotną stronę
                axis, shift = self.stage1_key(key)
                self.unscrambled_image = np.roll(self.scrambled_image, -shift, axis=axis)
            return True
        except Exception as e:
            print(f"Błąd odszyfrowania: {e}")
            return False

    # !!!!!!!!!!!!!!!!!!!! Etapy !!!!!!!!!!!!!!!!!!!!
    def stage_1(self, key):
        axis, shift = self.stage1_key(key)
        # np.roll przesuwa przez calą tablice o podanych parametrach
        self.scrambled_image = np.roll(self.original_image, shift, axis=axis)

    def stage_2(self, key):
        pass

    def stage_3(self, key):
        pass