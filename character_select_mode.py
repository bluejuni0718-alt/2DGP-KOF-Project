from pico2d import*
import game_framework
import play_mode


image = None
p1_image = None
p2_image = None

KEYMAP_P1 ={
    'left' :SDLK_a,
    'right':SDLK_d,
    'up'   :SDLK_w,
    'down' :SDLK_s,
    'lp'   :SDLK_f,
    'rp'   :SDLK_g,
    'rk'   :SDLK_b,
    'lk'   :SDLK_c
}
KEYMAP_P2 ={
    'left'  :SDLK_LEFT,
    'right' :SDLK_RIGHT,
    'up'    :SDLK_UP,
    'down'  :SDLK_DOWN,
    'lp'    :SDLK_KP_4,
    'rp'    :SDLK_KP_5,
    'rk'    :SDLK_KP_2,
    'lk'    :SDLK_KP_1
}

p1_x = 200
p1_y = 50
p2_x = 600
p2_y = 50
p_move_step = 175

def init():
    global image, p1_image, p2_image, p1_x, p1_y, p2_x, p2_y
    image = load_image('GameMode_Image/Game_Character_Select.png')
    p1_image = load_image('GameMode_Image/Game_Character_Select_Player.png')
    p2_image = load_image('GameMode_Image/Game_Character_Select_Player.png')
    p1_x, p1_y = 228, 242
    p2_x, p2_y = 575, 242
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
        elif event.type==SDL_KEYDOWN and event.key==SDLK_RETURN:
            game_framework.change_mode(play_mode)
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