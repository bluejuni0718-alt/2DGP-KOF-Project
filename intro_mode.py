import game_framework
from pico2d import*


def init():
    global image
    global running

    image = load_image('GameMode_Image/Game_Intro_Image.png')
    running = True

def finish():
    global image
    del image

def update():
    if running == False:
        game_framework.quit()
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
        if event.type== SDL_KEYDOWN:
            if event.key== SDLK_RETURN:
                running= False
    pass