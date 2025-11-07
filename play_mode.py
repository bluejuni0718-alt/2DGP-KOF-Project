from pico2d import *
from frame import *
import game_framework
from character import *
import game_world
import intro_mode

running = True

def handle_events():
    event_list = get_events()
    global running
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        elif event.type==SDL_KEYDOWN and event.key==SDLK_RETURN:
            game_framework.change_mode(intro_mode)
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
    game_world.clear()
    pass


