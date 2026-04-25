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
    def unscramble(self, stage, key, source="scrambled"):
        # Wybor
        target_image = self.original_image if source == "original" else self.scrambled_image
        if target_image is None:
            return False
        
        try:
            if stage == 1:        # Unscramble dla etapu 1 w odwrotną stronę
                self.unscrambled_image = self.stage_1_work(target_image, key, reverse=True)
            elif stage == 2 or stage == 3:      # Unscramble dla etapu 2
                seed = self.seed_from_key(key)

                # Zdjecie maski dla etapu 3
                if stage == 3:
                    # Ustawiamy seed
                    rng = np.random.default_rng(seed)

                    # Generujemy maskę o wymiarach przetasowanego obrazu
                    noise = rng.integers(0, 256, size=target_image.shape, dtype=np.int16)

                    # Mieniamy kod obrazu zgodnie z int16 (16 bitow), uniknąc limita 255 w kodzie kolorow
                    img_int = target_image.astype(np.int16)

                    # Odejmujemy maskę i robimy mod 256 zeby otrzymac kody kolorow
                    unscrambled = (img_int - noise) % 256

                    # Ustawiamy obraz
                    target_image = unscrambled.astype(np.uint8)

                # Dzialanie etapu 2 (Fisher-Yates)
                h, w, c = target_image.shape
                n = h * w     # Ilosc
                
                # Spłaszczamy obraz docelowy
                flat_img = target_image.reshape((n, c))
                
                # Odtwarzamy ten sam wektor przesunięć
                p = self.fisher_yates_permutation(n, seed)
                
                # Tworzymy puste canvas na odszyfrowane piksele
                unscrambled_flat = np.zeros_like(flat_img)
                
                # Umieszczamy piksele na ich oryginalnych indeksach p (Permutacja)
                unscrambled_flat[p] = flat_img
                
                # Zwijamy obraz z powrotem do 2D
                self.unscrambled_image = unscrambled_flat.reshape((h, w, c))

            return True
        except Exception as e:
            print(f"Błąd odszyfrowania: {e}")
            return False

    # !!!!!!!!!!!!!!!!!!!! Etapy !!!!!!!!!!!!!!!!!!!!
    # ---------------------------- Stage 1 ------------------------------
    def stage_1(self, key):
        self.scrambled_image = self.stage_1_work(self.original_image, key, reverse=False)
    
    def stage_1_work(self, image, key, reverse=False):
        axis, shift = self.stage1_key(key)
        if shift == 0:
            return image.copy()

        img = image.copy()
        h, w = img.shape[:2]
        
        # Otrzymanie dlugosci N (ilosci sektrorow)
        N = abs(shift)
        if shift > 0:
            sign = 1
        else:
            sign = -1
        
        # Ustalenie wymiaru do podziału (wysokość dla R, szerokość dla C)
        if axis == 1:
            length = h
        else:
            length = w
        
        # Zabezpieczenie N 
        N = min(N, length) 
        
        # Wyliczamy długość pojedynczego sektora
        sector_N = length // N
        
        for i in range(N):
            # Ustalanie początku i końca sektora
            start = i * sector_N
            # Jeśli to jest ostatni sektor, bierzemy wszystkie piksele do samego końca
            if i == N - 1:
                end = length
            # Else kończymy sektor normalnie
            else:
                end = (i + 1) * sector_N
            
            # Wyliczamy przesunięcie dla tego sektora
            shift2 = (abs(shift) - i) * sign
            
            # Odwrócenie kierunku, jeśli używamy tego do metody unscramble
            if reverse:
                shift2 = -shift2
                
            # Wykonujemy przesunięcie tylko dla konkretnego sektora obrazu
            if axis == 1: # Wiersze przemieszczają się po osi X
                img[start:end, :] = np.roll(img[start:end, :], shift2, axis=1) # Wyvina w pioziomie Wiersze
            else:         # Kolumny przemieszczają się po osi Y
                img[:, start:end] = np.roll(img[:, start:end], shift2, axis=0) # Wyvina w pionie Kolumny
                
        return img

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

    # ---------------------------- Stage 2 ------------------------------
    def stage_2(self, key):
        seed = self.seed_from_key(key)
        
        # Pobieramy wysokość(h), szerokość(w) i ilość kanałów koloru (c)
        h, w, c = self.original_image.shape
        n = h * w # Całkowita ilość pikseli na siatce
        
        # Każdy piksel staje się osobnym elementem w jednej długiej liście
        flat_img = self.original_image.reshape((n, c))
        
        # Generujemy wymieszaną tablicę indeksów z kluczem(seed)
        p = self.fisher_yates_permutation(n, seed)
        
        # Nakładamy wymieszane indeksy na canvas obrazu
        scrambled_flat = flat_img[p]
        
        # Formujemy z powrotem prostokąt i przypisujemy do zmiennej
        self.scrambled_image = scrambled_flat.reshape((h, w, c))

    # Zamienia klucza (string) na int
    def seed_from_key(self, key):
        try:
            # Próbuje potraktować klucz jako system szesnastkowy
            return int(key, 16) % (2**32)
        except ValueError:
            # Inaczej zamienia go na liczbę przez hashowanie
            return abs(hash(key)) % (2**32)

    # Generuje tablicę wymieszanych indeksów za pomocą algorytmu Fisher Yates
    def fisher_yates_permutation(self, n, seed):
        random.seed(seed)
        
        # Tworzymy tablice indeksów
        p = np.arange(n)
        
        # Algorytm Fisher-Yates
        for i in range(n - 1, 0, -1):
            j = random.randint(0, i)
            p[i], p[j] = p[j], p[i]
            
        return p

    # ---------------------------- Stage 3 ------------------------------
    def stage_3(self, key):
        # Dzialanie stadzu 2
        self.stage_2(key)

        seed = self.seed_from_key(key)
        # Tworzymy generator losowy na podstawie klucza
        rng = np.random.default_rng(seed)
        
        # Generujemy tablicę losowych wartości od 0 do 255 dla każdego piksela na 3 kanały RGB
        noise = rng.integers(0, 256, size=self.scrambled_image.shape, dtype=np.int16)

        # Rzutujemy oryginalny obraz na int16
        img_int = self.scrambled_image.astype(np.int16)
        
        # SZYFROWANIE
        scrambled = (img_int + noise) % 256
        
        # Zamiana na standardowy format pikseli
        self.scrambled_image = scrambled.astype(np.uint8)