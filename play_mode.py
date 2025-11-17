from pico2d import *
from frame import *
import game_framework
from character import *
import game_world
import intro_mode
from interaction import InteractionManager

def pico_renderer(left, bottom, right, top, color=None, tag=None):
    # 간단히 사각형 외곽을 그림. color/tag는 무시하거나 확장 가능.
    draw_rectangle(left, bottom, right, top)

interaction_manager = InteractionManager(renderer=pico_renderer)

interaction_manager.show_hitboxes = True

running = True

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
        else:
            test_character.handle_event(event)
    pass

def init():
    global test_character

    test_character = Character(KimFrameInfo())
    game_world.add_object(test_character)
    pass

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


