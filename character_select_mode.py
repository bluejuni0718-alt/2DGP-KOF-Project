from pico2d import*
import game_framework

image =None

def init():
    global image
    image= load_image('GameMode_Image/Game_Character_Select.png')
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
    clear_canvas()
    image.draw(400,300,800,600)
    update_canvas()
    pass

def update():
    pass

def pause():
    pass

def resume():
    pass