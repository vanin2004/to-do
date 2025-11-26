import random
import string

class SlugService:
    def generate_slug(self, length: int = 8) -> str:
        letters_and_digits = string.ascii_uppercase + string.digits


        return ''.join(random.choice(letters_and_digits) for _ in range(length))