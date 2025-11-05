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
    pass

def handle_events():
    pass