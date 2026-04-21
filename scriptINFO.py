# scriptINFO.py
import numpy as np

class ImageAnalyzer:
    @staticmethod

    # Zwraca procentowe podobieństwo dwóch obrazów piksel po pikselu
    def similarity(img1, img2):
        if img1 is None or img2 is None or img1.shape != img2.shape:
            return 0.0
        # Zlicza identyczne piksele i dzieli przez całkowitą ich liczbę
        match = np.sum(img1 == img2)
        total = img1.size
        return (match / total) * 100.0

    @staticmethod
    # Oblicza korelację sąsiednich pikseli w poziomie.
    def correlation(img):
        # Blisko 1 = płynny obraz. Blisko 0 = kompletny szum / chaos.
        if img is None: return 0.0
        # Konwersja do skali szarości
        gray = np.dot(img[...,:3], [0.2989, 0.5870, 0.1140]).flatten()
        if len(gray) < 2: return 0.0
        
        # Korelacja piksela n z pikselem n+1
        x = gray[:-1]
        y = gray[1:]
        # np.corrcoef zwraca macierz, ktora zamieniamy na wartość poza przekątną
        return np.corrcoef(x, y)[0, 1]

    @staticmethod
    # Zwraca listę 5 najpopularniejszych kolorów i ich ilość
    def top_5(img):
        if img is None: return []
        # Splaszczamy obraz do tablicy pikseli
        pixels = img.reshape(-1, 3)
        # Znajdujemy unikalne kolory i zliczamy je
        colors, counts = np.unique(pixels, axis=0, return_counts=True)
        
        # Sortujemy indeksy malejąco
        sorted_idx = np.argsort(-counts)
        
        top5 = []
        for i in range(min(5, len(colors))):
            idx = sorted_idx[i]
            top5.append((tuple(colors[idx]), counts[idx]))
        return top5