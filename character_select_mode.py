from pico2d import*
import game_framework

image =None

def init():
    global image
    image= load_image('character_select_mode.png')
    pass

def finish():
    global image
    del image
    pass

def handle_events():
    pass

def draw():
    pass