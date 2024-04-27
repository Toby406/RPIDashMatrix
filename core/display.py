import sys
from core import settings

#setup rgbmatrixlibary, fallback to virtual display if not found
sys.path.append(settings.rgbmatrixlib_path)
print("Loading rgbmatrix from: " + settings.rgbmatrixlib_path)

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
except:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions

#setup display
options: RGBMatrixOptions = RGBMatrixOptions()

#important options
options.drop_privileges = False
options.rows = settings.canvas_height
options.cols = settings.canvas_width
options.hardware_mapping = "regular"

options.gpio_slowdown = 3

#other options
options.daemon = False
options.show_refresh_rate = 0
# options.pwm_lsb_nanoseconds = 80
# options.limit_refresh_rate_hz = 150
options.brightness = settings.default_brightness

# Enable if you want to rotate the display 180 degrees
# options.pixel_mapper_config = "U-mapper;Rotate:180"

matrix: RGBMatrix = RGBMatrix(options=options)

#base display features

def toggle_display():
    settings.display_on = not settings.display_on
    if settings.debug:
        print("Display on: " + str(settings.display_on))

def decrease_brightness():
    settings.default_brightness = min(100, settings.default_brightness + 5)

def increase_brightness():
    settings.default_brightness = max(0, settings.default_brightness - 5)