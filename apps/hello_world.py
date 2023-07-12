from core import settings
from PIL import Image, ImageFont, ImageDraw

class HelloWorld:
    def __init__(self):
        self.font: ImageFont = ImageFont.truetype(settings.font_path, 5)

    def run(self):
        frame: Image = Image.new("RGB", (settings.canvas_width, settings.canvas_height), settings.background_color)
        canvas: ImageDraw = ImageDraw.Draw(frame)
        
        canvas.text((0, 0), "Hello World!", font=self.font, fill=settings.text_color)
        return frame