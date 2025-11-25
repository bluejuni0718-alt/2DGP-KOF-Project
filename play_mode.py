from pico2d import *
import game_framework
from character import Character, KimFrameInfo, hitbox_manager
import game_world
import intro_mode
from interaction import *


running = True
debug_hitbox = False
characters =[]
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


def handle_events():
    event_list = get_events()
    global running
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        elif event.type==SDL_KEYDOWN and event.key==SDLK_r:
            game_framework.change_mode(intro_mode)
        elif event.type==SDL_KEYDOWN and event.key == SDLK_F1:
            global debug_hitbox
            debug_hitbox = not debug_hitbox
        else:
            for c in characters:
                c.handle_event(event)
    pass

def init():
    global characters
    c1 = Character(KimFrameInfo(), keymap=KEYMAP_P1, x=100, y=120)
    c2 = Character(KimFrameInfo(), keymap=KEYMAP_P2, x=400, y=120)
    characters = [c1, c2]
    if c1.xPos < c2.xPos:
        c1.face_dir = 1
        c2.face_dir = -1
    else:
        c1.face_dir = -1
        c2.face_dir = 1

    for c in characters:
        game_world.add_object(c)

def update():
    game_world.update()

def draw():
    clear_canvas()
    game_world.render()
    if debug_hitbox:
        hitbox_manager.debug_draw()
    hitbox_manager.detect_body_overlaps()
    hitbox_manager.detect_is_opponent_attacking()
    hitbox_manager.update_face_dir(characters[0], characters[1])
    update_canvas()

def finish():
    game_world.clear()
    pass


