from core import settings
from apps import base_app
from PIL import Image, ImageDraw
from apis import db_api
from datetime import datetime, timezone

class BahnApp(base_app.BaseApp):
    
    
    def __init__(self):
        super().__init__()
        self.lastUpdate = datetime.now(timezone.utc)
        self.time = datetime.now(timezone.utc)
        self.abfahrt = db_api.get_next_departure()
        
        
    def update(self) -> bool:
        update = False
        
        time = datetime.now(timezone.utc)
        if((time - self.lastUpdate).seconds > 1):
            self.lastUpdate = time
            self.abfahrt = db_api.get_next_departure()
            update = True
        if(not settings.input.held):
            super().update()
        else:
            pass
        return update
             
    def generate(self) -> Image:
        frame: Image = Image.new("RGB", (settings.canvas_width, settings.canvas_height), settings.background_color)
        canvas: ImageDraw = ImageDraw.Draw(frame)
        
        depature = (self.abfahrt - datetime.now(timezone.utc)).seconds
        print("Abfahrt in {}:{}".format(depature // 60, depature % 60))
        
        # canvas.text((3, 6), "Nächste Abfahrt in: ", settings.light_pink, font=self.font)
        canvas.multiline_text((3, 6), "Nächste Abfahrt", settings.light_pink, font=self.font)
        #time
        canvas.text((3, 13), self.padToTwoDigit(depature // 60), settings.light_pink, font=self.font)
        canvas.text((10, 13), ":", settings.light_pink, font=self.font)
        canvas.text((13, 13), self.padToTwoDigit(depature % 60), settings.light_pink, font=self.font)
        super().postprocessing(frame)
        return frame
    
    def padToTwoDigit(self, num):
        if (num < 10):
            return "0" + str(num)
        else:
            return str(num)