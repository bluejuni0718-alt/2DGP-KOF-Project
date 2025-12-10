from pico2d import *
import game_framework
from character import Character
import game_world
import intro_mode
import common
from map import PalaceMap, Timer, HpBar, WinCount
from ai_controller import AIController
from character_frame import *
from interaction import HitBoxManager

running = True
debug_hitbox = False
round_over = False

ROUND_OVER_DELAY = 3.0
round_over_timer = 0.0
round_reset_timer = 0.0

def reset_round():
    global round_over, round_reset_timer
    round_over = False

    common.c1, common.c2 = common.characters

    if common.c1.hp <= 0 :
        common.c2.win_count += 1
    elif common.c2.hp <= 0 :
        common.c1.win_count += 1

    common.game_timer.total_time = 0.0
    common.c1.reset(100,120)
    common.c2.reset(700,120)
    common.c1.xPos = common.palace_map.w / 2 - 200
    common.c2.xPos = common.palace_map.w / 2 + 300
    common.palace_map.window_left = int(common.palace_map.w / 2 - common.palace_map.cw / 2)
    if common.c1.win_count >=2 or common.c2.win_count >=2:
        game_framework.change_mode(intro_mode)

    pass
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
        elif event.type==SDL_KEYDOWN and event.key == SDLK_F1: #히트박스 그리기
            global debug_hitbox
            debug_hitbox = not debug_hitbox
        elif event.type==SDL_KEYDOWN and event.key == SDLK_F2: #플레이어 공격력 최대치로 조절
            common.c1.atk = 100
            common.c2.atk = 100
            pass
        elif event.type==SDL_KEYDOWN and event.key==SDLK_F4: #타이머 종료
            common.game_timer.total_time = 117.0
        else:
            for c in common.characters:
                c.handle_event(event)
    pass

def init():
    common.palace_map = PalaceMap()
    common.game_timer = Timer()
    common.hitbox_manager = HitBoxManager()

    game_world.add_object(common.palace_map)
    game_world.add_object(common.game_timer, 1)
    # p1의 캐릭터 생성
    if common.p1_character_num == 0:
        common.c1 = Character(ShingoFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)
    elif common.p1_character_num == 1:
        common.c1 = Character(KimFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)
    elif common.p1_character_num == 2:
        common.c1 = Character(YuriFrameInfo(), keymap=common.KEYMAP_P1, x=100, y=120)

    # p2의 캐릭터 생성
    if common.game_mode == 'Two Player':
        if common.p2_character_num == 0:
            common.c2 = Character(ShingoFrameInfo(), keymap=common.KEYMAP_P2, x=700, y=120)
        elif common.p2_character_num == 1:
            common.c2 = Character(KimFrameInfo(), keymap=common.KEYMAP_P2, x=700, y=120)
        elif common.p2_character_num == 2:
            common.c2 = Character(YuriFrameInfo(), keymap=common.KEYMAP_P2, x=700, y=120)

    if common.stage_num == 0 and common.game_mode == 'Single Player':
        common.c2 = Character(KimFrameInfo(), keymap=common.KEYMAP_P2, x=700, y=120)
        common.ai_player = AIController(common.c2, common.c1)
    common.characters = [common.c1, common.c2]
    common.p1_HpBar = HpBar(common.c1, 175, 550)
    common.p2_HpBar = HpBar(common.c2, 625, 550)
    common.p1_win_counter = WinCount(common.c1, 280, 500)
    common.p2_win_counter = WinCount(common.c2, 487, 500)
    game_world.add_object(common.p1_HpBar, 1)
    game_world.add_object(common.p2_HpBar, 1)
    game_world.add_object(common.p1_win_counter, 1)
    game_world.add_object(common.p2_win_counter, 1)
    common.c1.xPos = common.palace_map.w/2 - 200
    common.c2.xPos = common.palace_map.w/2 + 300
    common.palace_map.window_left = int(common.palace_map.w/2 - common.palace_map.cw/2)
    if common.c1.xPos < common.c2.xPos:
        common.c1.face_dir = 1
        common.c2.face_dir = -1
    else:
        common.c1.face_dir = -1
        common.c2.face_dir = 1

    for c in common.characters:
        game_world.add_object(c)

def update():
    global round_over, round_over_timer,round_reset_timer
    game_world.update()

    common.c1, common.c2 = common.characters
    if common.game_mode == 'Single Player':
        common.ai_player.update()
        common.ai_player.run()
    if common.c1.hp <= 0 or common.c2.hp<=0:
        if not round_over:
            round_over = True
            round_over_timer = ROUND_OVER_DELAY
        else:
            round_over_timer -= game_framework.frame_time
            if round_over_timer <= 0.0:
                if common.c1.win_count >= 2 or common.c2.win_count >= 2:
                    game_framework.change_mode(intro_mode)
                else:
                    reset_round()
    elif common.game_timer.total_time >= 60.0:
        if not round_over:
            round_over = True
            round_over_timer = ROUND_OVER_DELAY
        else:
            round_over_timer -= game_framework.frame_time
            if round_over_timer <= 0.0:
                if common.c1.hp > common.c2.hp:
                    common.c1.win_count += 1
                elif common.c2.hp > common.c1.hp:
                    common.c2.win_count += 1
                if common.c1.win_count >= 2 or common.c2.win_count >= 2:
                    game_framework.change_mode(intro_mode)
                else:
                    reset_round()

    if common.hitbox_manager == None:
        common.hitbox_manager = HitBoxManager()

    # 이후 기존 호출들을 안전하게 호출
    if common.hitbox_manager:
        common.hitbox_manager.detect_body_overlaps()
        common.hitbox_manager.detect_is_opponent_attacking()
        common.hitbox_manager.update_face_dir(common.characters[0], common.characters[1])
        common.hitbox_manager.detect_attack_hits()

def draw():
    clear_canvas()
    game_world.render()
    if debug_hitbox:
        common.hitbox_manager.debug_draw()
    update_canvas()

def finish():
    game_world.clear()
    pass


