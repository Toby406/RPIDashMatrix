from core import settings
from apps import base_app
from PIL import Image, ImageFont, ImageDraw

class HelloApp(base_app.BaseApp):
    def __init__(self):
        super().__init__()
        
    def update(self):
        temp = self.need_update
        self.need_update = False
        return temp

    def generate(self) -> Image:
        frame: Image = Image.new("RGB", (settings.canvas_width, settings.canvas_height), settings.background_color)
        canvas: ImageDraw = ImageDraw.Draw(frame)
        
        canvas.text((0, 0), "Hello World!", font=self.font, fill=settings.text_color)
        return frame