from core import settings
from PIL import Image, ImageFont, ImageDraw

class BaseApp():
    def __init__(self):
        self.font: ImageFont = ImageFont.truetype(settings.font_path, 5)
        self.need_update: bool = True
    
    def update(self) -> bool:
        if (settings.input.value == settings.InputStatus.ENCODER_DECREASE):
            settings.current_vertical_app_id = (settings.current_vertical_app_id - 1) % len(settings.vertical_app_list)
            self.need_update = True
        elif (settings.input.value == settings.InputStatus.ENCODER_INCREASE):
            settings.current_vertical_app_id = (settings.current_vertical_app_id + 1) % len(settings.vertical_app_list)
            self.need_update = True
        else:
            self.need_update = False
        return self.need_update
    
    def generate(self) -> Image:
        return settings.blank_screen
    
    def postprocessing(self, frame:Image):
        canvas :ImageDraw = ImageDraw.Draw(frame)
        #add white border if held
        if(settings.input.held):
            canvas.rectangle([(0, 0), (settings.canvas_width - 1, settings.canvas_height - 1)], outline=(255, 255, 255))