import sys, signal, time
from core import settings, display
from apps import hello_world

from PIL import Image
def main():
    
    #setup apps
    vertical_app_list = [hello_world.HelloWorld()]
    
    frame: Image = settings.blank_screen
    
    #display loop
    while (True):
        if settings.display_on:
            frame = vertical_app_list[settings.current_vertical_app_id].run()
        else:
            frame = settings.blank_screen
        display.matrix.SetImage(frame)
        time.sleep(0.1)
        
#Setup interrupt with Ctrl-C
def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    main()
        
            
    