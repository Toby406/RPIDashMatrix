from core import settings
from PIL import Image, ImageFont, ImageDraw

class BaseApp():
    def __init__(self):
        self.font: ImageFont = ImageFont.truetype(settings.font_path, 5)
        self.need_update: bool = True
    
    def update(self) -> bool:
        return self.need_update
    
    def generate(self) -> Image:
        return settings.blank_screen