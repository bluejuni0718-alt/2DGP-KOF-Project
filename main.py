from pico2d import *
from frame import *
from character import *

isRun = True

open_canvas()
test_character = Character(KimFrameInfo())

def handle_events():
    event_list = get_events()
    global isRun
    for event in event_list:
        if event.type == SDL_QUIT:
            isRun = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            isRun = False
        else:
            test_character.handle_event(event)
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
