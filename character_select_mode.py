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
p1_rect = [0,0,32,33]
p2_rect = [67,0,32,33]
p1_selected = False
p2_selected = False
p_move_step = 175
min_x = 210
max_x = 580
def init():
    global image, p1_image, p2_image, p1_x, p1_y, p2_x, p2_y
    image = load_image('GameMode_Image/Game_Character_Select.png')
    p1_image = load_image('GameMode_Image/Game_Character_Select_Player.png')
    p2_image = load_image('GameMode_Image/Game_Character_Select_Player.png')
    p1_x, p1_y = 228, 242
    p2_x, p2_y = 575, 242
    pass

def finish():
    global image, p1_image, p2_image
    del image, p1_image, p2_image
    pass

def handle_events():
    global p1_rect, p2_rect, p1_selected, p2_selected
    event_list=get_events()
    for event in event_list:
        if event.type== SDL_QUIT:
            game_framework.quit()
        elif event.type==SDL_KEYDOWN:
            if event.key==KEYMAP_P1['left']:
                global p1_x
                if min_x < p1_x - p_move_step < max_x and p1_selected == False:
                    p1_x = p1_x - p_move_step
            elif event.key==KEYMAP_P1['right']:
                if min_x < p1_x + p_move_step < max_x and p1_selected == False:
                    p1_x = p1_x + p_move_step
            elif event.key==KEYMAP_P2['left']:
                global p2_x
                if min_x < p2_x - p_move_step < max_x and p2_selected == False:
                    p2_x = p2_x - p_move_step
            elif event.key==KEYMAP_P2['right']:
                if min_x < p2_x + p_move_step < max_x and p2_selected == False:
                    p2_x = p2_x + p_move_step
            elif event.key == KEYMAP_P1['lk']:
                p1_rect[0] = 35
                p1_selected = True
                pass
            elif event.key == KEYMAP_P2['lk']:
                p2_rect[0] = 100
                p2_selected = True
                pass
        elif p1_selected and p2_selected:
            game_framework.change_mode(play_mode)
    pass
#0,35,67,100
def draw():
    global image, p1_image, p2_image
    clear_canvas()
    image.draw(400,300,800,600)
    p1_image.clip_draw(p1_rect[0],p1_rect[1],p1_rect[2],p1_rect[3],p1_x,p1_y,100,115)
    p2_image.clip_draw(p2_rect[0],p2_rect[1],p2_rect[2],p2_rect[3], p2_x, p2_y,100,115)
    print(f'x: {p2_x}, y: {p2_y}')
    update_canvas()
    pass

def update():
    pass

def pause():
    pass

def resume():
    pass