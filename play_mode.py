from pico2d import *
from frame import *
import game_framework
from pico2d import *
from frame import *
import game_framework
from character import Character, KimFrameInfo
import game_world
import intro_mode
from interaction import InteractionManager

def pico_renderer(left, bottom, right, top, color=None, tag=None):
    # 간단히 사각형 외곽을 그림. color/tag는 무시하거나 확장 가능.
    draw_rectangle(left, bottom, right, top)

interaction_manager = InteractionManager(renderer=pico_renderer)

interaction_manager.show_hitboxes = True

running = True
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
        elif event.type == SDL_KEYDOWN and event.key == SDLK_h:
            # H 키로 히트박스 토글
            interaction_manager.show_hitboxes = not getattr(interaction_manager, 'show_hitboxes', True)
        else:
            for c in characters:
                c.handle_event(event)
    pass

def init():
    global characters
    c1 = Character(KimFrameInfo(), keymap=KEYMAP_P1, manager=interaction_manager, x=100, y=120)
    c2 = Character(KimFrameInfo(), keymap=KEYMAP_P2, manager=interaction_manager, x=400, y=120)
    characters = [c1, c2]
    for c in characters:
        game_world.add_object(c)

def update():
    game_world.update()

def draw():
    interaction_manager.begin_frame()
    clear_canvas()
    game_world.render()
    interaction_manager.process()
    if getattr(interaction_manager, 'show_hitboxes', False):
        interaction_manager.debug_draw()
    update_canvas()

def finish():
    game_world.clear()
    pass


