from core import settings
from apps import base_app
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
from dateutil import tz

class HomeApp(base_app.BaseApp):
    def __init__(self):
        super().__init__()
        self.bgs = {'sakura' : Image.open(settings.current_path + '/resources/backgrounds/sakura-bg.png').convert("RGB")
                    # 'cloud' : Image.open(settings.current_path + '/apps/res/main_screen/cloud-bg-clear.png').convert("RGBA"),
                    # 'forest' : Image.open(settings.current_path + '/apps/res/main_screen/forest-bg.png').convert("RGB")
                    }
        
        
        self.tz = tz.tzlocal()
        self.current_time:datetime = datetime.now(self.tz)
        self.last_minutes = self.current_time.minute
        
        
    def update(self) -> bool:
        self.current_time = datetime.now(self.tz)
        if(self.last_minutes != self.current_time.minute):
            self.last_minutes = self.current_time.minute
            return True
        if(not settings.input.held):
            super().update()
        else:
            pass
             
    def generate(self) -> Image:
        
        return self.generate_sakura()
    
    def padToTwoDigit(self, num):
        if (num < 10):
            return "0" + str(num)
        else:
            return str(num)
        
    def generate_sakura(self) -> Image:
        frame: Image = self.bgs['sakura'].copy()
        canvas: ImageDraw = ImageDraw.Draw(frame)
        
        
        #time
        canvas.text((3, 6), self.padToTwoDigit(self.current_time.hour), settings.light_pink, font=self.font)
        canvas.text((10, 6), ":", settings.light_pink, font=self.font)
        canvas.text((13, 6), self.padToTwoDigit(self.current_time.minute), settings.light_pink, font=self.font)

        #date
        canvas.text((23, 6), self.padToTwoDigit(self.current_time.month), settings.dark_pink, font=self.font)
        canvas.text((30, 6), ".", settings.dark_pink, font=self.font)
        canvas.text((33, 6), self.padToTwoDigit(self.current_time.day), settings.dark_pink, font=self.font)
        
        super().postprocessing(frame)
        return frame
    
