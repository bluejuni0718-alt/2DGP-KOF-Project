import game_framework
import character_select_mode
import common
from pico2d import *


def init():
    global image
    global running

    image = load_image('GameMode_Image/Game_Intro_Image.png')
    running = True

def finish():
    global image
    del image

def update():
    global running
    if running == False:
        game_framework.change_mode(character_select_mode)
    pass

def draw():
    clear_canvas()
    image.draw(400, 300, 800, 600)
    update_canvas()
    pass

def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        if event.type== SDL_KEYDOWN:
            if event.key== SDLK_1:
                common.game_mode = 'Single Player'
                running= False
            elif event.key == SDLK_2:
                common.game_mode = 'Two Player'
                running= False
    pass