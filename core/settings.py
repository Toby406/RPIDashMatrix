import configparser
from enum import Enum
import os
from PIL import Image

# Set path to main directory
current_path: str = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Set path to config file
config_path: str = current_path + "/config.ini"
print("Loading config from: " + config_path)

# Load config file
configs = configparser.ConfigParser()
parsed_configs: list[str] = configs.read(config_path)

# Check if config file was loaded
if len(parsed_configs) == 0:
    print("Error: Config file not found.")
    exit(1)

# Generate other paths from config file

font_path: str = current_path + configs["PATHS"]["font_path"]
rgbmatrixlib_path: str = current_path + configs["PATHS"]["rgbmatrixlib_path"]

# Load display settings

canvas_width: int = configs.getint("DISPLAY", "canvas_width", fallback=64)
canvas_height: int = configs.getint("DISPLAY", "canvas_height", fallback=32)
default_brightness: int = configs.getint("DISPLAY", "default_brightness", fallback=50)
blank_screen: Image = Image.new("RGB", (canvas_width, canvas_height), (0, 0, 0))

# Pin configuration
enc_switch: int = configs.getint("PINS", "enc_switch", fallback=5)
enc_A: int = configs.getint("PINS", "enc_A", fallback=13)
enc_B: int = configs.getint("PINS", "enc_B", fallback=6)
tilt: int = configs.getint("PINS", "tilt", fallback=26)

# Unit configuration
temp_unit: str = configs.get("UNITS", "temp_unit", fallback="C")

# Color configuration
text_color: tuple[int, int, int] = (255, 255, 255)
title_color: tuple[int, int, int] = (255, 255, 255)
artist_color: tuple[int, int, int] = (255, 255, 255)
play_color: tuple[int, int, int] = (255, 255, 255)
background_color: tuple[int, int, int] = (0, 0, 0)

# User preferences
#initial app id
current_horizontal_app_id: int = configs.getint("USER", "init_app_id", fallback=0)
current_vertical_app_id: int = configs.getint("USER", "init_app_id_v", fallback=0)


#Global variables
display_on = True

#Print debug messages
debug = True

#constants
class InputStatus(Enum):
    NOTHING = 1
    SINGLE_PRESS = 2
    DOUBLE_PRESS = 3
    TRIPLE_PRESS = 4
    LONG_PRESS = 5
    ENCODER_INCREASE = 6
    ENCODER_DECREASE = 7