import sys, signal, time
from core import settings, display, controls
from apps import hello_app, home_app

from PIL import Image
def main():
    
    #setup apps
    settings.vertical_app_list = [home_app.HomeApp(),hello_app.HelloApp()]
    
    frame: Image = settings.blank_screen
    
    #main loop
    while (True):
        #check if display needs to be updated
        update_display: bool = settings.vertical_app_list[settings.current_vertical_app_id].update() or settings.input.changed

        #update display
        if update_display:
            settings.input.value = settings.InputStatus.NOTHING
            if settings.debug:
                print("Updating display")
            if settings.display_on:
                frame = settings.vertical_app_list[settings.current_vertical_app_id].generate()
            else:
                frame = settings.blank_screen
        
        #display frame
        display.matrix.SetImage(frame)
        
        settings.input.changed = False
        
        #wait
        time.sleep(0.1)
        
#Setup interrupt with Ctrl-C
def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    main()
        
            
    