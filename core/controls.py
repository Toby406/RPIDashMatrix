import time
from core import settings
try:
    from gpiozero import Button
except:
    class Button:
        def __init__(self, num, pull_up=False):
            self.num = num
            self.pull_up = pull_up
            self.when_pressed = lambda : None
            self.when_pressed = lambda : None
            self.when_held = lambda : None
            self.when_released = lambda : None
            
#setup rotary encoder button
enc_button: Button = Button(settings.enc_switch, pull_up=False, bounce_time = 0.1)

enc_button.when_pressed = lambda: enc_button_pressed()
enc_button.when_released = lambda: enc_button_released()
enc_button.when_held = lambda : None

press_time: float = time.time()
release_time: float = time.time()

def long_press():
    if settings.debug:
        print("Held")
    # settings.input.value  = settings.InputStatus.LONG_PRESS
    settings.input.held = not settings.input.held
    
def enc_button_pressed():
    settings.input.pressed = True
    settings.input.changed = True
    
    # disable button callback
    enc_button.when_pressed = lambda : None
    
    # count more presses
    start_time: float = time.time()
    presses: int = 0
    last_pressed: bool = False
    
    # count presses
    while ((time.time() - start_time) < 0.3):
        if(enc_button.is_pressed):
            if(not last_pressed):
                presses += 1
                last_pressed = True
                if settings.debug:
                    print("Pressed")
                time.sleep(0.15)
                start_time = time.time()
        else:
            last_pressed = False
            
    # if button is still pressed, it was a long press
    if enc_button.is_active:
        long_press()
        enc_button.when_pressed = lambda: enc_button_pressed() 
        return

    if presses == 1:
        settings.input.value = settings.InputStatus.SINGLE_PRESS
    elif presses == 2:
        settings.input.value = settings.InputStatus.DOUBLE_PRESS
    elif presses == 3:
        settings.input.value = settings.InputStatus.TRIPLE_PRESS

    if settings.debug:
        if settings.input.value == settings.InputStatus.SINGLE_PRESS:
            print("Single press")
        elif settings.input.value == settings.InputStatus.DOUBLE_PRESS:
            print("Double press")
        elif settings.input.value == settings.InputStatus.TRIPLE_PRESS:
            print("Triple press")
    
    enc_button.when_pressed = lambda: enc_button_pressed()    
    
def enc_button_released():
    settings.input.pressed = False
    settings.input.changed = True
    

    



#setup tilt switch
tiltSwitch: Button = Button(settings.tilt, pull_up=True)
tiltSwitch.when_pressed = lambda: tilt()
tiltSwitch.when_released = lambda: tilt()
def tilt():
    startTime = time.time()
    while (time.time() - startTime < 0.4): # wait for ball to settle
        pass
    if settings.debug:
        pass
        # print("Tilt" + tiltSwitch.is_pressed.__str__())
    settings.input.horizontal = tiltSwitch.is_pressed
    settings.input.changed = True




#setup rotary encoder
from core.encoder import Encoder
encoder = Encoder(settings.enc_A, settings.enc_B)

