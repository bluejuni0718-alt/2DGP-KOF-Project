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
    global world
    global test_character

    world = []

    world.append(test_character)
    pass

def update_world():
    for o in world:
        o.update()
    pass
    pass

def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()
    pass

reset_world()

while isRun:
    handle_events()
    update_world()
    render_world()
    delay(0.1)
close_canvas()
