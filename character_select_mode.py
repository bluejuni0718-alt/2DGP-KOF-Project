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
    event_list=get_events()
    for event in event_list:
        if event.type== SDL_QUIT:
            game_framework.quit()
        elif event.type==SDL_KEYDOWN and event.key==SDLK_ESCAPE:
            game_framework.quit()
    pass

def draw():
    pass