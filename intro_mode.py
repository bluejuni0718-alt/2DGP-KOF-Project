from pico2d import*

image = None
running= True

def init():
    global image, running
    image = load_image('Game_Intro_Image.png')
    running = True
    pass

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

    pass