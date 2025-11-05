from pico2d import *
from frame import *
from character import *
import game_world

isRun = True

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

def init():
    global test_character

    test_character = Character(KimFrameInfo())
    game_world.add_object(test_character)
    pass

def update():
    game_world.update()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    pass


