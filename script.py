import random

class ImageProcessor:
    def __init__(self):
        self.image_path = None
        self.original_image = None
        self.scrambled_image = None
        self.unscrambled_image = None

    # Random Key
    def generate_random_key(self):
        """Generuje losowy 16-znakowy klucz HEX."""
        return "".join(random.choices("0123456789ABCDEF", k=16))
    
