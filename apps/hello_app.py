from core import settings
from apps import base_app
from PIL import Image, ImageFont, ImageDraw
from copy import deepcopy

class HelloApp(base_app.BaseApp):
    
    
    def __init__(self):
        super().__init__()
        
        
    def update(self) -> bool:
        if(not settings.input.held):
            super().update()
        else:
            pass
             
    def generate(self) -> Image:
        frame: Image = Image.new("RGB", (settings.canvas_width, settings.canvas_height), settings.background_color)
        canvas: ImageDraw = ImageDraw.Draw(frame)
        
        canvas.text((0, 0), "Hello World!", font=self.font, fill=settings.text_color)
        super().postprocessing(frame)
        return frame