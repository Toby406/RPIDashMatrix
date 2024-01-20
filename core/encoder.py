import RPi.GPIO as GPIO
from core import settings

class Encoder:
    
    def __init__(self, leftPin: int, rightPin: int):
        # referring to the pins by the "Broadcom SOC channel" number
        GPIO.setmode(GPIO.BCM)
        
        # define the Encoder switch Inputs
        self.leftPin: int = leftPin
        self.rightPin: int = rightPin
        
        # setup pins as input with pull-up resistors
        GPIO.setup(self.leftPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.rightPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                
        # event detection with debounce, interrupt
        GPIO.add_event_detect(self.leftPin, GPIO.BOTH, callback=self.update)
        GPIO.add_event_detect(self.rightPin, GPIO.BOTH, callback=self.update)
        
        # initialize counter and last state variables
        self.last_state: tuple[bool, bool] = (0, 0)
        self.current_direction: str = ""
    
    def update(self, channel):
        settings.input.changed = True
        # get current switch positions
        new_state: tuple[bool, bool] = (GPIO.input(self.leftPin), GPIO.input(self.rightPin))
        # compare current switch positions to the last known positions
        
        #default state
        if self.last_state == (0,0):
            if new_state == (0,1):
                self.current_direction = "right"
            elif new_state == (1,0):
                self.current_direction = "left"
                
        #Was turned Right one quarter or turned left three quarters
        elif self.last_state == (0,1):
            if new_state == (1,1): # Turned right another quarter
                self.current_direction = "right"
            elif new_state == (0,0): # Turned left full step
                if self.current_direction == "left":
                    self.left()
        
        #Was turned left one quarter or turned right three quarters
        elif self.last_state == (1,0):
            if new_state == (1,1): # Turned left another quarter
                self.current_direction = "left"
            elif new_state == (0,0): # Turned right full step
                if self.current_direction == "right":
                    self.right()
        
        #Half step "elif self.last_state == (1,1):"
        else:
            if new_state == (0,1): # Turned left another quarter
                self.current_direction = "left"
            elif new_state == (1,0): # Turned right another quarter
                self.current_direction = "right"
            elif new_state == (0,0): #Skipped something
                if self.current_direction == "left":
                    self.left()
                elif self.current_direction == "right":
                    self.right()            
        self.last_state = new_state
    
    def left(self):
        if(settings.debug):
            print("Encoder left")
        settings.input.value = settings.InputStatus.ENCODER_DECREASE
        
    
    def right(self):
        if(settings.debug):
            print("Encoder right")
        settings.input.value  = settings.InputStatus.ENCODER_INCREASE
    
    def getDirection(self) -> str:
        return self.current_direction
    
    

        
