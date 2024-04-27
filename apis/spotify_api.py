import spotipy
import threading
import os, time
import requests_cache
from core import settings

#cache specific requests
# def checkID(response):
#     #print(str('"type" : "track"' in response.text) + str(response))
#     #print('"volume_percent"' in response.text)
#     return '"type" : "track"' in response.text #or '"volume_percent":' in response.text
# requests_cache.install_cache(cache_name='spotipy_cache', expire_after=1, filter_fn=checkID, use_memory=True)
# requests_cache.clear()

CACHE = '.auth'

class SpotifyApi:
    def __init__(self, config):
        self.invalid = False
        self.resetCache = 0

        if 'Spotify' in config:
            client_id = config['Spotify']['client_id']
            client_secret = config['Spotify']['client_secret']
            redirect_uri = config['Spotify']['redirect_uri']

            if client_id and client_secret and redirect_uri:
                try:
                    scope = "user-read-currently-playing, user-read-playback-state, user-modify-playback-state"
                    print("\n\n\n")
                    self.auth_manager = spotipy.SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope, cache_path=CACHE, open_browser=False)
                    # print("Spotify Api:", self.auth_manager.get_authorize_url())
                    print("\n\n\n")
                    
                    self.sp = spotipy.Spotify(auth_manager=self.auth_manager, requests_timeout=10)
                    self.track = None
                    self.isPlaying = False
                    self.track = self.sp.current_user_playing_track()

                    threading.Thread(None, self.updateCache).start()

                except Exception as e:
                    print(e)
                    self.invalid = True
            else:
                print("Spotify Api: Empty Spotify client id or secret")
                self.invalid = True
    
    def updateCache(self):
        while True:
            try:
                self.forceUpdateCache()
            except Exception as e:
                print("Spotify Api cache:"  + str(e))
            time.sleep(2)
            
    def forceUpdateCache(self):
        print("Spotify Api: update cache")
        settings.input_disabled = False
        self.track = self.sp.current_user_playing_track()
        
    def isInvalid(self):
        return self.invalid

    def getCurrentPlayback(self):
        if self.invalid:
            return None
        try:
            track = self.track
            if (track is not None):
                if (track['item'] is None):
                    artist = None
                    title = None
                    art_url = None
                else:
                    artist = track['item']['artists'][0]['name']
                    if len(track['item']['artists']) >= 2:
                        artist = artist + ", " + track['item']['artists'][1]['name']
                    title = track['item']['name']
                    art_url = track['item']['album']['images'][0]['url']
                self.isPlaying = track['is_playing']
                return (artist, title, art_url, self.isPlaying, track["progress_ms"], track["item"]["duration_ms"])
            else:
                return None
        except Exception as e:
            print("Spotify Api: Exception getting current song ", e)
            return None
    
    def resume_playback(self):
        if not self.invalid:
            try:
                self.sp.start_playback()
                print("Spotify Api: resume from active device")
            except spotipy.exceptions.SpotifyException:
                print("Spotify Api: no active, trying device 1")
                devices = self.sp.devices()
                if 'devices' in devices and len(devices['devices']) > 0:
                    try:
                        self.sp.start_playback(device_id = devices['devices'][1]['id'])
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)
    
    def pause_playback(self):
        if not self.invalid:
            try:
                self.sp.pause_playback()
            except Exception as e:
                print("Spotify Api: problem pausing playback", e)

    def next_track(self):
        if not self.invalid:
            try:
                self.sp.next_track()
            except spotipy.exceptions.SpotifyException:
                print('no active, trying specific device')
                devices = self.sp.devices()
                if 'devices' in devices and len(devices['devices']) > 0:
                    self.sp.next_track(device_id = devices['devices'][0]['id'])
            except Exception as e:
                print(e)

    def previous_track(self):
        if not self.invalid:
            try:
                self.sp.previous_track()
            except spotipy.exceptions.SpotifyException:
                print('no active, trying specific device')
                devices = self.sp.devices()
                if 'devices' in devices and len(devices['devices']) > 0:
                    self.sp.previous_track(device_id = devices['devices'][0]['id'])
            except Exception as e:
                print("Spotify Api: ", e)
    
    def active_devices(self, devices):
        
        active_devices = filter(lambda irgendwie: irgendwie['is_active'], devices)
        return list (active_devices)
        
    def increase_volume(self):
        if not self.invalid and self.isPlaying:
            try:
                devices = self.sp.devices()
                active_device = self.active_devices(devices['devices'])
                print(active_device)
                curr_volume = active_device[0]['volume_percent']
                #curr_volume -= curr_volume%5
                self.sp.volume(min(100, curr_volume + 5))
            except Exception as e:
                print("Spotify Api: Exception increasing volume ", e)

    def decrease_volume(self):
        if not self.invalid and self.isPlaying:
            try:
                devices = self.sp.devices()
                active_device = self.active_devices(devices['devices'])
                print(active_device)
                curr_volume = active_device[0]['volume_percent']
                #curr_volume -= curr_volume%5
                self.sp.volume(max(0, curr_volume - 5))
            except Exception as e:
                print("Spotify Api: Exception lowering volume ",e)
                
    def set_volume(self, volume):
        if not self.invalid and self.isPlaying:
                try:
                    self.sp.volume(volume)
                except Exception as e:
                    print("Spotify Api: Exception setting volume ",e)
    
    def get_volume(self):
        if not self.invalid and self.isPlaying:
            try:
                devices = self.sp.devices()
                active_device = self.active_devices(devices['devices'])
                #print("VolumeAPI:" , active_device[0]['volume_percent'])
                return active_device[0]['volume_percent']
            except Exception as e:
                print("Spotify Api: Exception getting volume ",e)
                return 10
        else:
            print("Spotify Api: not playing default volume 10")
            return 10
        


    