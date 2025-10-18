from pico2d import *
from frame import *
from character import *

isRun = True

open_canvas()
test_character = Character(KimFrameInfo())

def handle_events():
    pass

def reset_world():
    pass

def update_world():
    pass

def render_world():
    pass

reset_world()

while isRun:
    handle_events()
    update_world()
    render_world()
    delay(0.1)
close_canvas()
