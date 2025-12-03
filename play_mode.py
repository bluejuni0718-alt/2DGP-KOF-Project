from pico2d import *
import game_framework
from character import Character, KimFrameInfo, hitbox_manager
import game_world
import intro_mode
import common
from interaction import *


running = True
debug_hitbox = False


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
            for c in common.characters:
                c.handle_event(event)
    pass

def init():
    c1 = Character(KimFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)
    c2 = Character(KimFrameInfo(), keymap=common.KEYMAP_P2, x=700, y=120)
    common.characters = [c1, c2]
    if c1.xPos < c2.xPos:
        c1.face_dir = 1
        c2.face_dir = -1
    else:
        c1.face_dir = -1
        c2.face_dir = 1

    for c in common.characters:
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
    hitbox_manager.update_face_dir(common.characters[0], common.characters[1])
    hitbox_manager.detect_attack_hits()
    update_canvas()

def finish():
    game_world.clear()
    pass


