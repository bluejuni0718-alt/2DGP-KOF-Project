from pico2d import*

image = None
running= True

def init():
    global image, running
    image = load_image('Game_Intro_Image.png')
    running = True

def finish():
    global image
    del image

def update():
    pass

def draw():
    clear_canvas()
    image.draw(800, 600)
    update_canvas()
    pass

def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type== SDL_KEYDOWN:
            if event.key==SDLK_KP_ENTER:
                running= False
    pass