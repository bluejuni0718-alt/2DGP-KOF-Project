from pico2d import *
import character_frame

characters = []
palace_map = None
game_timer = None
p1_win_counter = None
p2_win_counter = None
p1_HpBar = None
p2_HpBar = None
c1 = None
c2 = None
game_mode = None
hitbox_manager = None
ai_player = None
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

#todo: 다른 캐릭터 이미지 프레임 정보 여기다 넣기?