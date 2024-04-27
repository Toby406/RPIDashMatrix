from core import settings
from apps import base_app
from apis import spotify_api

from PIL import Image, ImageDraw
import cutlet
import requests
import threading
from io import BytesIO

class SpotifyApp(base_app.BaseApp):
    def __init__(self):
        super().__init__()
        self.spotify = spotify_api.SpotifyApi(settings.configs)
        
        self.last_respone = None
        self.last_art_url = None
        self.art_img = Image.new("RGB", (settings.canvas_height, settings.canvas_height), settings.background_color)
        self.is_playing, self.progress_ms, self.duration_ms, self.response, self.art_url, self.artist, self.title = False, 1, 1, "", "", "", ""
        self.artist_animation_cnt, self.title_animation_cnt = 0, 0
        
        self.animation_speed = 1;
        self.katsu = cutlet.Cutlet()
        
        self.update_image_event = threading.Event()
        threading.Thread(None, self.update_image_async).start()
        
        
    def update(self) -> bool:
        update = self.update_api()
        if(not settings.input.held):
            update = super().update()
        elif(not settings.input_disabled):
            #control mode
            if (settings.input.value == settings.InputStatus.SINGLE_PRESS):
                settings.input_disabled = True
                if self.is_playing:
                    self.spotify.pause_playback()
                else:
                    self.spotify.resume_playback()                    
            
            if(settings.input.pressed and settings.input.value == settings.InputStatus.ENCODER_INCREASE):
                self.animation_speed = min(2, self.animation_speed + 1)   
            elif(settings.input.value == settings.InputStatus.ENCODER_INCREASE):
                self.spotify.increase_volume()
            
            if(settings.input.pressed and settings.input.value == settings.InputStatus.ENCODER_DECREASE):
                self.animation_speed = max(0, self.animation_speed - 1)
                self.artist_animation_cnt = 0
                self.title_animation_cnt = 0
            elif(settings.input.value == settings.InputStatus.ENCODER_DECREASE):
                self.spotify.decrease_volume()
            
            if(settings.input.value == settings.InputStatus.DOUBLE_PRESS):
                self.spotify.next_track()
                
            if(settings.input.value != settings.InputStatus.NOTHING):
                update = True
                self.spotify.forceUpdateCache()
            
        return True
    
    def update_image_async(self):
        while True:
            self.update_image_event.wait()
            self.update_image_event.clear()
            print("image updated")
            try:
                response = requests.get(self.art_url)
                img = Image.open(BytesIO(response.content))
                self.art_img = img.resize((settings.canvas_height, settings.canvas_height), resample=Image.LANCZOS)    
            except:
                pass
             
             
    def generate(self) -> Image:
        frame: Image = Image.new("RGB", (settings.canvas_width, settings.canvas_height), settings.background_color)
        canvas: ImageDraw = ImageDraw.Draw(frame)
        self.drawPlayPause(canvas)
        
        #draw progress bar
        canvas.line((38,17,57,17), fill=(100,100,100))
        canvas.line((38,17,38+round(((self.progress_ms / self.duration_ms) * 100) // 5),17), fill=(180,180,180))
        
        #draw artist
        self.draw_artist(canvas)
        
        #draw title
        self.draw_title(canvas)
        
        canvas.rectangle((0,0,33,32), fill=(0,0,0))
        
        #draw image
        if self.art_img is not None:
            frame.paste(self.art_img, (0,0))
            
        if(not settings.input.horizontal):
            rotatedFrame: Image = Image.new("RGB", (settings.canvas_width, settings.canvas_height), settings.background_color)
            rotatedFrame.paste(frame.rotate(90, expand=True), (0, -settings.canvas_height))
            rotatedFrame.paste(frame.rotate(90, expand=True), (settings.canvas_height, 0))
            rotatedFrame.save('./lol.png', quality=95)
            frame = rotatedFrame
        
        super().postprocessing(frame)
        return frame
    

    def update_api(self) -> bool:
        self.response = self.spotify.getCurrentPlayback()
        if(self.response is not None):
            (self.artist,self.title,self.art_url,self.is_playing, self.progress_ms, self.duration_ms) = self.response
        self.translate()
        if(self.last_art_url != self.art_url):
            self.last_art_url = self.art_url
            self.update_image_event.set()
            return True
        if(self.last_respone != self.response):
            self.last_respone = self.response
            return True

    def drawPlayPause(self, canvas):
        if not self.is_playing:
            canvas.line((45,21,45,27), fill = settings.play_color)
            canvas.line((46,22,46,26), fill = settings.play_color)
            canvas.line((47,22,47,26), fill = settings.play_color)
            canvas.line((48,23,48,25), fill = settings.play_color)
            canvas.line((49,23,49,25), fill = settings.play_color)
            canvas.line((50,24,50,24), fill = settings.play_color)
        else:
            canvas.line((45,21,45,27), fill = settings.play_color)
            canvas.line((46,21,46,27), fill = settings.play_color)
            canvas.line((49,21,49,27), fill = settings.play_color)
            canvas.line((50,21,50,27), fill = settings.play_color)
        
    def draw_artist(self, canvas):
        artist_len = self.font.getlength(self.artist)
        if artist_len > 31:
            spacer = "     "
            canvas.text((34-self.artist_animation_cnt, 9), self.artist + spacer + self.artist, settings.artist_color, font = self.font)
            self.artist_animation_cnt += self.animation_speed
            if self.artist_animation_cnt >= self.font.getlength(self.artist + spacer):
                self.artist_animation_cnt = 0
        else:
            self.artist_animation_cnt = 0
            canvas.text((34-self.artist_animation_cnt, 9), self.artist, settings.artist_color, font = self.font)

    def draw_title(self, canvas):
        title_len = self.font.getlength(self.title)
        if title_len > 31:
            spacer = "   "
            canvas.text((34-self.title_animation_cnt, 2), self.title + spacer + self.title, settings.title_color, font = self.font)
            self.title_animation_cnt += self.animation_speed
            if self.title_animation_cnt >= self.font.getlength(self.title + spacer):
                self.title_animation_cnt = 0
        else:
            self.title_animation_cnt = 0
            canvas.text((34-self.title_animation_cnt, 2), self.title, settings.title_color, font = self.font)
            
    def translate(self):
        # self.artist = self.artist.translate(special_char_map)
        backup = self.artist
        self.artist = self.katsu.romaji(self.artist)
        if self.artist.__contains__("????"):
            self.artist = backup
        
        backup = self.title
        self.title = self.katsu.romaji(self.title)
        if self.title.__contains__("????"):
            self.title = backup
        



"""
from matrix import settings, controls
import threading, time, asyncio
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
from dateutil import tz
import requests, requests_cache
from io import BytesIO

session = requests_cache.CachedSession(cache_name='spotify_image_cache', expire_after=2)

class SpotifyScreen:
    def __init__(self):
        

        self.apis = settings.apis
        self.default_actions = controls.default_actions
        spotify_api = self.apis['spotify']
        
        self.font = ImageFont.truetype(settings.font_path, 5)
        self.canvas_width = settings.canvas_width #config.getint('System', 'canvas_width', fallback=64)
        self.canvas_height = settings.canvas_height #config.getint('System', 'canvas_height', fallback=32)
        self.title_color = settings.title_color
        self.artist_color = settings.artist_color
        self.play_color = settings.play_color

        self.current_art_url = ''
        self.art_url = ''
        self.current_art_img = None
        self.current_title = ''
        self.current_artist = ''
        self.katsu = cutlet.Cutlet()
        
        self.title_animation_cnt = 0
        self.artist_animation_cnt = 0

        self.is_playing = False
        self.control_mode = False
        self.apiVolume = 10
        self.volume = 30
        self.fadetimer = -1
        threading.Thread(None, self.update_async).start()
        #threading.Thread(None, self.get_volume_from_api).start()
        
    def update_async(self):
        while True:
            if (self.current_art_url != self.art_url):
                print("image updated")
                self.current_art_url = self.art_url
                response = requests.get(self.current_art_url)
                img = Image.open(BytesIO(response.content))
                self.current_art_img = img.resize((self.canvas_height, self.canvas_height), resample=Image.LANCZOS)
            time.sleep(1)
    
    def get_volume_from_api(self):
        self.apiVolume = self.apis['spotify'].get_volume() #TODO:VOLUME SHIT
        
    def set_volume_to_api(self, volume):
        if (self.control_mode and self.is_playing and volume != self.apiVolume):
            print("self", volume, "api", self.apiVolume)
            self.apis['spotify'].set_volume(volume)
            self.apiVolume = self.apis['spotify'].get_volume()
            print("afterget self", volume, "api", self.apiVolume)
    
    def generate(self, isHorizontal, inputStatus):
        if (inputStatus is settings.InputStatus.LONG_PRESS):
            self.control_mode = not self.control_mode


        spotify_api = self.apis['spotify']

        
        if not self.control_mode:
            if (inputStatus is settings.InputStatus.SINGLE_PRESS):
                self.default_actions['toggle_display']()
                self.title_animation_cnt = 0
                self.artist_animation_cnt = 0
            elif (inputStatus is settings.InputStatus.ENCODER_INCREASE):
                self.default_actions['switch_next_app']()
            elif (inputStatus is settings.InputStatus.ENCODER_DECREASE):
                self.default_actions['switch_prev_app']()
        else:
            if((inputStatus is settings.InputStatus.ENCODER_DECREASE or inputStatus is settings.InputStatus.ENCODER_INCREASE) and self.fadetimer == -1):
                #threading.Thread(None, self.get_volume_from_api).start()
                print("Spotify: volume updated")
                self.apiVolume = self.apis['spotify'].get_volume() #TODO:VOLUME SHIT
                self.volume = self.apiVolume - self.apiVolume%5
            #play pause
            if (inputStatus is settings.InputStatus.SINGLE_PRESS):
                if self.is_playing:
                    spotify_api.pause_playback()
                else:
                    spotify_api.resume_playback()
            #skip        
            elif (inputStatus is settings.InputStatus.DOUBLE_PRESS):
                spotify_api.next_track()
                
            #back    
            elif (inputStatus is settings.InputStatus.TRIPLE_PRESS):
                spotify_api.previous_track()
            
            #Change Volume
            elif (inputStatus is settings.InputStatus.ENCODER_INCREASE and self.is_playing):
                self.volume = min(100, self.volume + 5)
                self.fadetimer = 10
                threading.Thread(None, self.set_volume_to_api, args=(self.volume, )).start()
                #spotify_api.increase_volume()
            elif (inputStatus is settings.InputStatus.ENCODER_DECREASE and self.is_playing):
                self.volume = max(0, self.volume - 5)
                self.fadetimer = 10
                #spotify_api.decrease_volume()
       
        if (self.fadetimer == 0):
            threading.Thread(None, self.set_volume_to_api, args=(self.volume, )).start()
            
        self.fadetimer = max(-1, self.fadetimer - 1)     
        
        response = spotify_api.getCurrentPlayback()
        #print(response)
        if response is not None:
            (artist,title,art_url,self.is_playing, progress_ms, duration_ms) = response
            self.art_url = art_url
            spcial_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
            artist = artist.translate(spcial_char_map)
            artist = self.katsu.romaji(artist)
            title= title.translate(spcial_char_map)
            title = self.katsu.romaji(title)
            if (self.current_title != title or self.current_artist != artist):
                self.current_artist = artist
                self.current_title = title
                self.title_animation_cnt = 0
                self.artist_animation_cnt = 0
            #moved to update_image thread
            # if self.current_art_url != art_url:
            #     self.current_art_url = art_url

            #     response = requests.get(self.current_art_url)
            #     img = Image.open(BytesIO(response.content))
            #     self.current_art_img = img.resize((self.canvas_height, self.canvas_height), resample=Image.LANCZOS)

            frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0,0,0))
            draw = ImageDraw.Draw(frame)

            draw.line((38,15,58,15), fill=(100,100,100))
            draw.line((38,15,38+round(((progress_ms / duration_ms) * 100) // 5),15), fill=(180,180,180))
            if self.fadetimer >= 0: draw.text((57,27), str(self.volume), self.title_color, font = self.font)
               
            title_len = self.font.getsize(self.current_title)[0]
            if title_len > 31:
                spacer = "   "
                draw.text((34-self.title_animation_cnt, 0), self.current_title + spacer + self.current_title, self.title_color, font = self.font)
                self.title_animation_cnt += 1
                if self.title_animation_cnt == self.font.getsize(self.current_title + spacer)[0]:
                    self.title_animation_cnt = 0
            else:
                draw.text((34-self.title_animation_cnt, 0), self.current_title, self.title_color, font = self.font)

            artist_len = self.font.getsize(self.current_artist)[0]
            if artist_len > 31:
                spacer = "     "
                draw.text((34-self.artist_animation_cnt, 7), self.current_artist + spacer + self.current_artist, self.artist_color, font = self.font)
                self.artist_animation_cnt += 1
                if self.artist_animation_cnt == self.font.getsize(self.current_artist + spacer)[0]:
                    self.artist_animation_cnt = 0
            else:
                draw.text((34-self.artist_animation_cnt, 7), self.current_artist, self.artist_color, font = self.font)

            draw.rectangle((32,0,33,32), fill=(0,0,0))

            if self.current_art_img is not None:
                frame.paste(self.current_art_img, (0,0))
                
            self.drawPlayPause(draw, self.control_mode, self.is_playing, self.play_color)
            self.draw_time(draw)
            return frame
        else:
            #not active
            frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0,0,0))
            draw = ImageDraw.Draw(frame)
            self.current_art_url = ''
            self.art_url = ''
            self.is_playing = False
            self.drawPlayPause(draw, self.control_mode, self.is_playing, self.play_color)
            draw.text((0,3), "No Devices", self.title_color, font = self.font)
            draw.text((0,10), "Currently Active", self.title_color, font = self.font)
            self.draw_time(draw)
            return frame
        

        
    def draw_time(self, draw):
        currentTime = datetime.now(tz=tz.tzlocal())
        hours = currentTime.hour
        minutes = currentTime.minute
        draw.text((33, 27), padToTwoDigit(hours), self.title_color, font=self.font)
        draw.text((40, 27), ":", self.title_color, font=self.font)
        draw.text((43, 27), padToTwoDigit(minutes), self.title_color, font=self.font)

    def drawPlayPause(self, draw, control_mode, is_playing, color):
        if not is_playing:
            draw.line((45,19,45,25), fill = color)
            draw.line((46,20,46,24), fill = color)
            draw.line((47,20,47,24), fill = color)
            draw.line((48,21,48,23), fill = color)
            draw.line((49,21,49,23), fill = color)
            draw.line((50,22,50,22), fill = color)
        else:
            draw.line((45,19,45,25), fill = color)
            draw.line((46,19,46,25), fill = color)
            draw.line((49,19,49,25), fill = color)
            draw.line((50,19,50,25), fill = color)
def padToTwoDigit(num):
    if num < 10:
        return "0" + str(num)
    else:
        return str(num)
"""