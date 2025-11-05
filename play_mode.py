from pico2d import *
from frame import *
from character import *
import game_world

running = True

def handle_events():
    event_list = get_events()
    global running
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
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


