from pico2d import *

import game_framework
from interaction import *
from state_machine import *
from character_frame import *
from character_frame import CHARACTER_WIDTH_SCALE, CHARACTER_HEIGHT_SCALE
import common

hitbox_manager = HitBoxManager()



PIXEL_PER_METER = 10.0/0.15 #10 픽셀당 30cm로 설정

GRAVITY_MPS2 = -9.8 * 5
GRAVITY_PPS2 = GRAVITY_MPS2 * PIXEL_PER_METER  # px/s^2 (음수)

MAX_JUMP_HEIGHT = 4.0 #최대 점프 높이 4미터
MAX_JUMP_HEIGHT_PX = MAX_JUMP_HEIGHT * PIXEL_PER_METER #픽셀로 환산

RUN_SPEED_KMPH = 20.0 #시속 20km로 설정
RUN_SPEED_MPS = (RUN_SPEED_KMPH * 1000.0 / 3600.0) #초속미터 환산
RUN_SPEED_PPS = (RUN_SPEED_MPS*PIXEL_PER_METER) #초속 픽셀로 환산

WALK_SPEED_KMPH = 5
WALK_SPEED_MPS = (WALK_SPEED_KMPH * 1000.0 / 3600.0)
WALK_SPEED_PPS = (WALK_SPEED_MPS * PIXEL_PER_METER)

JUMP_SPEED_KMPH = 50
JUMP_SPEED_MPS = (JUMP_SPEED_KMPH * 1000.0 / 3600.0)
JUMP_SPEED_PPS = (JUMP_SPEED_MPS * PIXEL_PER_METER)

BACK_DASH_SPEED_KMPH = 20
BACK_DASH_SPEED_MPS = (BACK_DASH_SPEED_KMPH * 1000.0 / 3600.0)
BACK_DASH_SPEED_PPS = (BACK_DASH_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0/TIME_PER_ACTION
FRAMES_PER_ACTION = 8

JUMP_TIME_PER_ACTION = 0.8
JUMP_ACTION_PER_TIME = 1.0 / JUMP_TIME_PER_ACTION
FRAMES_PER_JUMP_ACTION = 5

MOVE_JUMP_TIME_PER_ACTION = 0.6
MOVE_JUMP_ACTION_PER_TIME = 1.0 / MOVE_JUMP_TIME_PER_ACTION
FRAMES_PER_MOVE_JUMP_ACTION = 5

BACK_DASH_TIME_PER_ACTION = 0.3
BACK_DASH_ACTION_PER_TIME = 1.0 / BACK_DASH_TIME_PER_ACTION
FRAMES_PER_BACK_DASH_ACTION = 6

ATTACK_TIME_PER_ACTION = 0.6
ATTACK_ACTION_PER_TIME = 1.0 / ATTACK_TIME_PER_ACTION
FRAMES_PER_ATTACK_ACTION = 6

COMBO_TIME_PER_ACTION = 0.6
COMBO_ACTION_PER_TIME = 1.0 / COMBO_TIME_PER_ACTION
FRAMES_PER_COMBO_ACTION = 8

def time_out(e):
    return e[0] == 'TIME_OUT'

def pressing_key(e):
    return e[0] == 'Pressing_Key'

def pressing_down(e):
    return e[0] == 'Pressing_Down'

def land(e):
    return e[0] == 'LAND'

def in_air(e):
    return e[0] == 'IN_AIR'

def guard(e):
    return e[0] == 'GUARD'

def hitted(e):
    return e[0] == 'HITTED'

def enable_combo(e):
    return e[0] == 'ENABLE_COMBO'

def dead(e):
    return e[0] == 'DEAD'


class Idle:
    def __init__(self, character):
        self.character =character
        pass
    def enter(self, e):
        self.character.anim_tick=0
        self.character.frame =0
        self.character.jump_frame=0
        pass
    def exit(self,e):
        pass
    def do(self):
        if self.character.is_opponent_attacking and self.character.back_pressed:
            self.character.state_machine.handle_state_event(('GUARD', None))
            return
        self.character.frame = (self.character.frame + FRAMES_PER_ACTION * ACTION_PER_TIME*game_framework.frame_time) % self.character.image.idle_frames
        if self.character.is_hitted :
            self.character.state_machine.handle_state_event(('HITTED', None))
            return

    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.update_hitbox(self.character.body_hitbox, int(self.character.frame))
        self.character.image.draw_idle_by_frame_num(int(self.character.frame), sx, self.character.yPos,self.character.face_dir)
        pass

class Walk:
    def __init__(self, character):
        self.character=character
    def enter(self, e):
        self.character.frame = 0

        if self.character.face_dir ==1:
            if self.character.fwd_down(e) or self.character.fwd_pressed:
                self.character.dir = 1
            elif self.character.back_down(e) or self.character.back_pressed:
                self.character.dir = -1
        else:
            if self.character.fwd_down(e) or self.character.fwd_pressed:
                self.character.dir = -1
            elif self.character.back_down(e) or self.character.back_pressed:
                self.character.dir = 1
        self.character.vx = self.character.dir * WALK_SPEED_PPS
        pass
    def exit(self,e):
        self.character.dir=0
        self.character.vx = 0
        pass
    def do(self):
        if self.character.is_opponent_attacking and self.character.back_pressed:
            self.character.state_machine.handle_state_event(('GUARD', None))
            return

        self.character.frame = (self.character.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % self.character.image.walk_frames
        self.character.xPos +=self.character.dir * WALK_SPEED_PPS * game_framework.frame_time
        pass
    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.update_hitbox(self.character.body_hitbox, self.character.image.walk_frame_start + int(self.character.frame))
        self.character.image.draw_by_frame_num(self.character.image.walk_frame_start + int(self.character.frame),sx, self.character.yPos,self.character.face_dir)
        pass

class Jump:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = 0
        self.character.dir=0
        self.character.ground_y = self.character.default_ground_y
        # 처음 점프일 때만 vy 설정 (TIME_OUT으로 다시 들어올 때 재설정하지 않음)
        if not (e and e[0] == 'TIME_OUT'):
            g_abs = abs(GRAVITY_PPS2)
            self.character.vy = (2 * g_abs * MAX_JUMP_HEIGHT_PX) ** 0.5
            if self.character.vy < 0:
                self.character.vy = -self.character.vy

    def exit(self, e):
        self.character.dir = 0
        self.character.frame = 0

    def do(self):
        self.character.frame += (FRAMES_PER_JUMP_ACTION * JUMP_ACTION_PER_TIME * game_framework.frame_time)
        self.character.vy += GRAVITY_PPS2 * game_framework.frame_time
        self.character.yPos += self.character.vy * game_framework.frame_time

        if self.character.is_opponent_attacking and self.character.back_pressed:
            self.character.state_machine.handle_state_event(('GUARD', None))
            return
        if self.character.yPos <= self.character.ground_y:
            self.character.vy = 0.0
            self.character.ground_y = self.character.default_ground_y
            self.character.yPos = self.character.default_ground_y
            if self.character.fwd_pressed or self.character.back_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Key', None))
            elif self.character.down_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Down', None))
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))


    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.update_hitbox(self.character.body_hitbox, self.character.image.jump_frame_start + int(self.character.frame))
        self.character.image.draw_by_frame_num(
            self.character.image.jump_frame_start + int(self.character.frame),
            sx, self.character.yPos, self.character.face_dir)

class MoveJump:
    def __init__(self, character):
        self.character = character
    def enter(self, e):
        self.character.frame = 0
        self.character.ground_y = self.character.default_ground_y
        if not (e and e[0] == 'TIME_OUT'):
            g_abs = abs(GRAVITY_PPS2)
            self.character.vy = (2 * g_abs * MAX_JUMP_HEIGHT_PX) ** 0.5
            if self.character.vy < 0:
                self.character.vy = -self.character.vy

        # 방향 결정 (기존 로직 유지)
        if self.character.face_dir == 1:
            if self.character.fwd_down(e) or self.character.fwd_pressed:
                self.character.dir = 1
            elif self.character.back_down(e) or self.character.back_pressed:
                self.character.dir = -1
        else:
            if self.character.fwd_down(e) or self.character.fwd_pressed:
                self.character.dir = -1
            elif self.character.back_down(e) or self.character.back_pressed:
                self.character.dir = 1
        self.character.vx = self.character.dir * WALK_SPEED_PPS

    def exit(self, e):
        self.character.frame = 0
    def do(self):
        if self.character.is_opponent_attacking and self.character.back_pressed:
            self.character.state_machine.handle_state_event(('GUARD', None))
            return
        if self.character.dir == 1:
            self.character.frame += self.character.face_dir * FRAMES_PER_MOVE_JUMP_ACTION * MOVE_JUMP_ACTION_PER_TIME * game_framework.frame_time
        else:
            self.character.frame -= self.character.face_dir * FRAMES_PER_MOVE_JUMP_ACTION * MOVE_JUMP_ACTION_PER_TIME * game_framework.frame_time

        self.character.vy += GRAVITY_PPS2 * game_framework.frame_time
        self.character.yPos += self.character.vy * game_framework.frame_time
        self.character.xPos += self.character.vx * game_framework.frame_time

        if self.character.yPos <= self.character.ground_y:
            self.character.ground_y = self.character.default_ground_y
            self.character.yPos = self.character.default_ground_y
            self.character.vy = 0.0
            if self.character.fwd_pressed or self.character.back_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Key', None))
            elif self.character.down_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Down', None))
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.update_hitbox(self.character.body_hitbox, self.character.image.jump_move_motion_list[int(self.character.frame)])
        self.character.image.draw_by_frame_num(
            self.character.image.jump_move_motion_list[int(self.character.frame)],
            sx, self.character.yPos, self.character.face_dir)

class Run:
    def __init__(self, character):
        self.character=character
    def enter(self, e):
        self.character.frame = 0

        if self.character.face_dir == 1:
            if self.character.fwd_down(e) or self.character.fwd_pressed:
                self.character.dir = 1
            elif self.character.back_down(e) or self.character.back_pressed:
                self.character.dir = -1
        else:
            if self.character.fwd_down(e) or self.character.fwd_pressed:
                self.character.dir = -1
            elif self.character.back_down(e) or self.character.back_pressed:
                self.character.dir = 1
        self.character.vx = self.character.dir * RUN_SPEED_PPS
        pass
    def exit(self,e):
        self.character.dir = 0
        self.character.vx = 0
        pass
    def do(self):
        self.character.frame = (self.character.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % self.character.image.run_frames
        self.character.xPos += self.character.dir * RUN_SPEED_PPS * game_framework.frame_time
    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.update_hitbox(self.character.body_hitbox, self.character.image.run_frame_start + int(self.character.frame))
        self.character.image.draw_by_frame_num(self.character.image.run_frame_start + int(self.character.frame),sx, self.character.yPos,self.character.face_dir)
        pass

class RunJump:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        # 기준 바닥 고정
        self.character.ground_y = self.character.default_ground_y
        # 초기 수직속도를 캐릭터 속성으로 설정 (모든 상태가 동일한 vy를 보게 됨)
        g_abs = abs(GRAVITY_PPS2)
        vy = (2 * g_abs * MAX_JUMP_HEIGHT_PX) ** 0.5
        if vy < 0:
            vy = -vy
        self.character.vy = vy
        # 방향 결정 (기존)
        if self.character.face_dir == 1:
            self.character.dir = 1
        else:
            self.character.dir = -1
        self.character.vx = self.character.dir * RUN_SPEED_PPS
    def exit(self, e):
        self.character.frame = 0

    def do(self):
        if self.character.is_opponent_attacking and self.character.back_pressed:
            self.character.state_machine.handle_state_event(('GUARD', None))
            return
        if int(self.character.frame)< len(self.character.image.jump_move_motion_list) - 1:
            self.character.frame += FRAMES_PER_MOVE_JUMP_ACTION * MOVE_JUMP_ACTION_PER_TIME * game_framework.frame_time
        else:
            self.character.frame = len(self.character.image.jump_move_motion_list) - 1

        # vertical: 항상 character.vy 사용
        self.character.vy += GRAVITY_PPS2 * game_framework.frame_time
        self.character.yPos += self.character.vy * game_framework.frame_time

        # horizontal
        self.character.xPos += self.character.vx * game_framework.frame_time

        if self.character.yPos <= self.character.ground_y:
            # 착지 시 기본 바닥으로 복원
            self.character.ground_y = self.character.default_ground_y
            self.character.yPos = self.character.default_ground_y
            self.character.vy = 0.0
            if self.character.fwd_pressed or self.character.back_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Key', None))
            elif self.character.down_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Down', None))
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.update_hitbox(self.character.body_hitbox, self.character.image.jump_move_motion_list[int(self.character.frame)])
        self.character.image.draw_by_frame_num(self.character.image.jump_move_motion_list[int(self.character.frame)],
                                               sx, self.character.yPos, self.character.face_dir)

class BackDash:
    def __init__(self, character):
        self.character = character
        self.vy = 0.0
    def enter(self, e):
        self.character.ground_y = self.character.yPos
        g_abs = abs(GRAVITY_PPS2)
        self.vy = (2 * g_abs * MAX_JUMP_HEIGHT_PX/10) ** 0.5
        if self.vy < 0:
            self.vy = -self.vy
        if self.character.face_dir == 1:
            self.character.dir = -1
        else:
            self.character.dir = 1
    def exit(self, e):
        self.character.dir = 0
        pass

    def do(self):
        self.vy += GRAVITY_PPS2 * game_framework.frame_time
        self.character.yPos += self.vy * game_framework.frame_time
        self.character.xPos += self.character.dir * BACK_DASH_SPEED_PPS * game_framework.frame_time

        if self.character.yPos <= self.character.ground_y:
            self.character.yPos = self.character.ground_y
            self.character.vy = 0.0
            if self.character.fwd_pressed or self.character.back_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Key', None))
            elif self.character.down_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Down', None))
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.update_hitbox(self.character.body_hitbox, self.character.image.back_dash_frame_start)
        self.character.image.draw_by_frame_num(self.character.image.back_dash_frame_start,
                                               sx, self.character.yPos, self.character.face_dir)

class SitDown:
    def __init__(self, character):
        self.character = character
        # 내부 sticky 상태: SitAttack에서 돌아와서 마지막 프레임을 유지해야 할 때 True
        self.fix_last_frame = False

    def enter(self, e):
        # SitAttack에서 돌아올 때 마지막 프레임 고정
        self.character.is_sit = True
        if self.character.keep_sit_down_last_frame:
            self.character.frame = 2
            self.character.keep_sit_down_last_frame = False
            self.fix_last_frame = True
        else:
            self.character.frame = 0
            self.fix_last_frame = False
    def exit(self, e):
        self.character.frame = 0
        self.character.is_sit = False
        self.fix_last_frame = False

    def do(self):
        if self.character.is_opponent_attacking and self.character.back_pressed:
            self.character.state_machine.handle_state_event(('GUARD', None))
            return
        if self.fix_last_frame:
            self.character.frame=2
        else:
            if self.character.frame <2:
                self.character.frame = (self.character.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % self.character.image.sit_down_frames

    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.update_hitbox(self.character.body_hitbox, self.character.image.sit_down_frame_start + int(self.character.frame))
        self.character.image.draw_by_frame_num(
            self.character.image.sit_down_frame_start + int(self.character.frame),
            sx,
            self.character.yPos - 6 * int(self.character.frame),
            self.character.face_dir)

class SitUp:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = self.character.image.sit_down_frames - 1
        pass
    def exit(self,e):
        self.character.frame = 0
        pass

    def do(self):
        # 프레임을 역재생으로 감소시킴
        delta = FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        self.character.frame -= delta
        if self.character.frame <= 0.0:
            # 완료되면 TIME_OUT으로 상태 전환
            self.character.frame = 0.0
            self.character.state_machine.handle_state_event(('TIME_OUT', None))
    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.update_hitbox(self.character.body_hitbox, self.character.image.sit_down_frame_start + int(self.character.frame))
        self.character.image.draw_by_frame_num(self.character.image.sit_down_frame_start + int(self.character.frame), sx, self.character.yPos - 6 * int(self.character.frame),self.character.face_dir)
        pass

class NormalAttack:
    def __init__(self, character):
        self.character = character
        self.attack_key = None
        self.frames = None
        self.frame_count = 0

    def enter(self, e):
        self.character.frame = 0.0
        self.character.is_attacking = True
        for k in ('rp', 'lp', 'rk', 'lk'):
            if e[1].key == self.character.keymap.get(k):
                self.attack_key = k
                break
        self.frames = self.character.image.normal_attacks.get(self.attack_key, {}).get('frames', [])
        self.frame_count = len(self.frames)
    def exit(self, e):
        self.character.frame = 0.0
        self.character.is_attacking = False
        self.character.is_succeeded_attack = False
        self.character.attack_hitbox.rect = (0, 0, 0, 0)
        self.attack_key = None

    def do(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.frame += FRAMES_PER_ATTACK_ACTION * ATTACK_ACTION_PER_TIME * game_framework.frame_time
        if self.character.is_succeeded_attack == False:
            self.character.attack_hitbox.rect = (sx + (25 * self.character.face_dir), self.character.yPos, 75 * self.character.face_dir, 100)
        else:
            self.character.attack_hitbox.reset_rect()
        if int(self.character.frame) >= self.frame_count:
            if self.character.rk_pressed and self.character.is_succeeded_attack and (get_time() - self.character._last_down[self.character.keymap['rk']] < 0.2):
                self.character.is_enable_combo = True
                self.character.combo_count += 1
                self.character.state_machine.handle_state_event(('ENABLE_COMBO', None))
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.image.draw_by_frame_num(self.frames[int(self.character.frame)], sx,
                                               self.character.yPos, self.character.face_dir)

class AirAttack:
    def __init__(self, character):
        self.character = character
        self.attack_key = None
        self.frames = None
        self.frame_count =0

    def enter(self, e):
        self.character.frame = 0.0
        self.character.is_attacking = True
        for k in ('rp', 'lp', 'rk', 'lk'):
            if e[1].key == self.character.keymap.get(k):
                self.attack_key = k
                break
        if self.character.dir != 0:
            self.frames = self.character.image.move_jump_attacks.get(self.attack_key, {}).get('frames', [])
        else:
            self.frames = self.character.image.jump_attacks.get(self.attack_key, {}).get('frames', [])
        self.frame_count = len(self.frames)

    def exit(self, e):
        self.character.dir = 0
        self.character.is_attacking = False
        self.character.is_succeeded_attack = False
        self.character.frame = 0.0
        self.character.attack_hitbox.rect = (0, 0, 0, 0)
        self.attack_key = None

    def do(self):
        # 애니 진행 및 중력 처리
        if int(self.character.frame)<self.frame_count - 1:
            self.character.frame += FRAMES_PER_ATTACK_ACTION * ATTACK_ACTION_PER_TIME * game_framework.frame_time
            if self.character.is_succeeded_attack == False:
                self.character.attack_hitbox.rect = (self.character.xPos + (25 * self.character.face_dir),
                                                     self.character.yPos, 75 * self.character.face_dir, 100)
            else:
                self.character.attack_hitbox.reset_rect()
            self.character.vy += GRAVITY_PPS2 * game_framework.frame_time
            self.character.yPos += self.character.vy * game_framework.frame_time
        else:
            self.character.attack_hitbox.rect = (0,0,0,0)
            self.character.dir = 0
            self.character.state_machine.handle_state_event(('TIME_OUT', None))
        # 착지 처리
        if self.character.yPos <= self.character.ground_y:
            self.character.dir = 0
            self.character.attack_hitbox.rect = (0,0,0,0)
            self.character.ground_y = self.character.default_ground_y
            self.character.yPos = self.character.default_ground_y
            self.character.vx = 0.0
            self.character.vy = 0.0
            self.character.state_machine.handle_state_event(('LAND', None))
        self.character.xPos += self.character.vx * game_framework.frame_time
    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.update_hitbox(self.character.body_hitbox,
                                     self.character.image.jump_move_motion_list[int(self.character.frame)])
        self.character.image.draw_by_frame_num(self.frames[int(self.character.frame)], sx,
                                               self.character.yPos, self.character.face_dir)

class SitAttack:
    def __init__(self, character):
        self.character = character
        self.attack_key = None
        self.frames=[]
        self.offset = None
        self.frame_count = 0
        self.character.attack_hitbox.rect = (0, 0, 0, 0)
    def enter(self, e):
        self.character.is_sit = True
        self.character.frame = 0.0
        for k in ('rp', 'lp', 'rk', 'lk'):
            if e[1].key == self.character.keymap.get(k):
                self.attack_key = k
                break
        self.frames = self.character.image.sit_attacks.get(self.attack_key, {}).get('frames', [])
        self.offset = self.character.image.sit_attacks.get(self.attack_key, {}).get('offsets', [])
        self.frame_count = len(self.frames)
    def exit(self, e):
        self.character.frame = 0.0
        self.character.is_sit = False
        self.attack_key = None
        self.character.attack_hitbox.rect = (0, 0, 0, 0)
        self.character.is_succeeded_attack =False
        if self.character.down_pressed:
            self.character.keep_sit_down_last_frame = True
        else:
            self.character.keep_sit_down_last_frame = False

    def do(self):
        self.character.frame += FRAMES_PER_ATTACK_ACTION * ATTACK_ACTION_PER_TIME * game_framework.frame_time
        if self.character.is_succeeded_attack == False:
            self.character.attack_hitbox.rect = (self.character.xPos + (25 * self.character.face_dir),
                                                 self.character.yPos - 75, 75 * self.character.face_dir, 100)
        else:
            self.character.attack_hitbox.reset_rect()

        if int(self.character.frame) >= self.frame_count:
            self.character.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        ox, oy = self.offset[int(self.character.frame)]
        self.character.image.draw_by_frame_num(self.frames[int(self.character.frame)],
                                               sx + (self.character.face_dir*ox),
                                               self.character.yPos + oy, self.character.face_dir)

class Guard:
    def __init__(self, character):
        self.character = character
        self.state = None
        self.frames = []
        self.frame_count = 0
    def enter(self, e):
        self.character.frame = 0
        if self.character.vy != 0:
            self.state = 'air_guard'
        if self.character.vy == 0 and self.character.is_sit == False:
            self.state = 'ground_guard'
        if self.character.back_pressed and self.character.down_pressed and self.character.vy == 0:
            self.character.is_low_guard = True
            self.state = 'sit_guard'
        self.frames = self.character.image.guards.get(self.state, {}).get('frames', [])
        self.frame_count = len(self.frames)
        # 가드 진입 시 공격 플래그 해제하고 가드 상태 설정
        self.character.is_attacking = False
        self.character.is_guarding = True

    def exit(self, e):
        self.character.is_guarding= False
        self.character.is_low_guard = False
        self.character.frame = 0.0

    def do(self):
        if not self.character.is_opponent_attacking or not self.character.back_pressed:
            if self.character.fwd_pressed or self.character.back_pressed:
                if self.character.vy == 0 and self.state != 'sit_guard':
                    self.character.state_machine.handle_state_event(('Pressing_Key', None))
            if self.state == 'air_guard':
                self.character.state_machine.handle_state_event(('TIME_OUT', None))
            if self.character.back_pressed and self.character.down_pressed:
                self.character.keep_sit_down_last_frame = True
                self.character.state_machine.handle_state_event(('Pressing_Down', None))

        if self.character.vy !=0 and int(self.character.frame) >= self.frame_count - 1:
            self.character.vy += GRAVITY_PPS2 * game_framework.frame_time
            self.character.yPos += self.character.vy * game_framework.frame_time

        if int(self.character.frame) >= self.frame_count - 1:
            self.character.frame = self.frame_count - 1  # 마지막 프레임에 고정

        self.character.frame += FRAMES_PER_ATTACK_ACTION * ATTACK_ACTION_PER_TIME * game_framework.frame_time

    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.image.draw_by_frame_num(self.frames[int(self.character.frame)],
                                               sx,
                                               self.character.yPos, self.character.face_dir)

class GetHit:
    def __init__(self, character):
        self.character = character
        self.state = None
        self.frames = []
        self.frame_count = 0
    def enter(self,e):
        self.character.frame = 0.0
        self.character.get_damage = True
        if self.character.vy == 0:
            if self.character.is_sit:
                self.state = 'low_hitted'
            else:
                self.state = 'middle_hitted'
        else:
            self.state = 'air_hitted'
        self.frames = self.character.image.hitted_motions.get(self.state, {}).get('frames', [])
        self.frame_count = len(self.frames)

        # 공중 피격이면 즉시 약간의 상향 임펄스와 수평 넉백 적용 (튜닝 가능)
        if self.state == 'air_hitted':
            knockback_speed = 200  # 필요시 값 조정
            self.character.vx = -self.character.face_dir * knockback_speed
        pass
    def exit(self,e):
        self.character.frame = 0
        self.character.is_hitted = False
        self.character.get_damage = True
        pass
    def do(self):
        self.character.frame += FRAMES_PER_ATTACK_ACTION * ATTACK_ACTION_PER_TIME * game_framework.frame_time
        if self.state == 'air_hitted':
            if self.frame_count > 0 and self.character.frame > (self.frame_count - 1):
                self.character.frame = int(self.frame_count - 1)
                if self.character.hp<=0:
                    self.character.state_machine.handle_state_event(('DEAD', None))
                    return
            self.character.vy += GRAVITY_PPS2 * game_framework.frame_time
            self.character.yPos += self.character.vy * game_framework.frame_time
            self.character.xPos += self.character.vx * game_framework.frame_time

            if self.character.yPos <= self.character.ground_y:
                # 착지 처리
                self.character.yPos = self.character.ground_y
                self.character.vy = 0.0
                self.character.vx = 0.0
                self.character.get_damage = True
                self.character.is_hitted = False
                self.character.state_machine.handle_state_event(('TIME_OUT', None))
                self.character.frame = 0.0
        else:
            # 지상 피격: 애니 끝나면 복귀
            if int(self.character.frame) >= self.frame_count - 1:
                self.character.is_hitted = False
                self.character.get_damage = True
                if self.character.hp<=0:
                    self.character.state_machine.handle_state_event(('DEAD', None))
                    return
                else:
                    self.character.state_machine.handle_state_event(('TIME_OUT', None))
                self.character.frame = 0.0
        pass
    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.update_hitbox(self.character.body_hitbox,
                                     self.character.image.jump_move_motion_list[int(self.character.frame)])
        self.character.image.draw_by_frame_num(self.frames[int(self.character.frame)],
                                               sx,
                                               self.character.yPos, self.character.face_dir)
        pass

class ComboAttack:
    def __init__(self, character):
        self.character = character
        self.attack_key = None
        self.frames = []
        self.frame_count = 0
        self.enable_combo_time = 0
    def enter(self, e):
        self.character.frame = 0
        self.character.is_attacking = True
        self.character.is_succeeded_attack = False
        self.attack_key = e[1]
        self.enable_combo_time = get_time() - self.character._last_down[self.character.keymap['rk']]
        if self.character.combo_count == 1:
            self.frames = self.character.image.combo_motions.get('combo_1', {}).get('frames', [])
            self.character.xPos += 50 * self.character.face_dir
        elif self.character.combo_count == 2:
            self.frames = self.character.image.combo_motions.get('combo_2', {}).get('frames', [])
            self.character.xPos += 50 * self.character.face_dir
        elif self.character.combo_count == 3:
            self.character.atk = 10  # 마지막 콤보 공격의 공격력 증가
            self.character.xPos += 75 * self.character.face_dir
            self.frames = self.character.image.combo_motions.get('combo_3', {}).get('frames', [])
        else:
            self.character.state_machine.handle_state_event(('TIME_OUT', None))
            self.character.combo_count = 0
            return
        self.frame_count = len(self.frames)

    def exit(self,e):
        self.character.frame = 0
        self.character.is_attacking = False
        self.character.attack_hitbox.rect = (0, 0, 0, 0)
        self.character.is_succeeded_attack = False
        self.character.atk = 5  # 콤보 공격 후 기본 공격력으로 복원
        if self.character.combo_count > 3 or not self.character.is_enable_combo:
            self.character.combo_count = 0
    def do(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.frame += FRAMES_PER_COMBO_ACTION * COMBO_ACTION_PER_TIME * game_framework.frame_time
        if self.character.is_succeeded_attack == False and int(self.character.frame) == self.frame_count // 2:
            self.character.attack_hitbox.rect = (sx + (25 * self.character.face_dir), self.character.yPos,
                                                    75 * self.character.face_dir, 100)
        else:
            self.character.attack_hitbox.reset_rect()
        if int(self.character.frame) >= self.frame_count and self.character.combo_count < 4:
            if self.character.is_succeeded_attack and self.enable_combo_time < 0.1:
                self.character.is_enable_combo = True
                self.character.combo_count += 1
                self.character.state_machine.handle_state_event(('ENABLE_COMBO', None))
                self.character.is_succeeded_attack = False
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))
                self.character.combo_count = 0
                self.character.frame = 0
                self.character.is_attacking = False
                self.character.attack_hitbox.rect = (0, 0, 0, 0)
                self.character.is_succeeded_attack = False

    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.image.draw_by_frame_num(self.frames[int(self.character.frame)],
                                               sx,
                                               self.character.yPos, self.character.face_dir)

class Dead:
    def __init__(self, character):
        self.character = character
    def enter(self, e):
        self.character.frame = 0.0
        pass
    def exit(self,e):
        self.character.frame = 0
        pass
    def do(self):
            self.character.frame = self.character.image.dead_frame
    def draw(self):
        sx = self.character.xPos - common.palace_map.window_left - 50 - 1
        self.character.image.draw_by_frame_num(self.character.image.dead_frame,sx, self.character.yPos,self.character.face_dir)
        pass

class Character:
    def __init__(self, image_data,keymap=None, x = 400, y = 120):
        default = {'left': SDLK_a, 'right': SDLK_d, 'up': SDLK_w,'down':SDLK_s,'lp':SDLK_f,'rp':SDLK_g,'rk':SDLK_b,'lk':SDLK_c}
        self.font = load_font('ENCR10B.TTF', 16)
        self.keymap = default if keymap is None else {**default, **keymap}
        self.hp = 100
        self.atk = 5
        self.xPos = x
        self.yPos = y
        self.vy = 0.0
        self.vx = 0.0
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.image=image_data
        self.jump_frame=0
        self.default_ground_y = self.yPos
        self.ground_y = self.default_ground_y
        self.double_tap_interval=0.3
        self.is_sit = False
        self.is_low_guard = False
        self.is_succeeded_attack = False
        self.is_enable_combo = False
        self.combo_count = 0
        self.get_damage = True

        self._last_down = {}  # key_const -> 마지막 다운 시각
        self._last_up = {}  # key_const -> 마지막 업 시각

        for k in ('left', 'right', 'up', 'down', 'lp', 'rp', 'lk', 'rk'):
            key_const = self.keymap[k]
            self._last_down[key_const] = 0.0
            self._last_up[key_const] = 0.0

        self.manager = hitbox_manager
        self.body_hitbox = self.register_hitbox('body', 0)
        self.attack_hitbox = HitBox(self, 'attack', (0, 0, 0, 0))
        self.manager.register_hitbox(self.attack_hitbox)

        self.fwd_pressed = False
        self.back_pressed = False
        self.down_pressed = False
        self.rk_pressed = False

        self.keep_sit_down_last_frame = False
        self.time_out_and_down = lambda e: (e[0] == 'TIME_OUT') and self.down_pressed
        self.time_out_and_not_down = lambda e: (e[0] == 'TIME_OUT') and (not self.down_pressed)
        self.can_combo = lambda e: (e[0] == 'ENABLE_COMBO') and self.is_enable_combo

        self.is_attacking = False
        self.is_opponent_attacking = False

        self.is_guarding = False
        self.is_hitted = False

        self.IDLE=Idle(self)
        self.WALK=Walk(self)
        self.JUMP=Jump(self)
        self.MOVE_JUMP=MoveJump(self)
        self.RUN = Run(self)
        self.RUN_JUMP = RunJump(self)
        self.BACK_DASH = BackDash(self)
        self.SIT_DOWN = SitDown(self)
        self.SIT_UP = SitUp(self)
        self.NORMAL_ATTACK = NormalAttack(self)
        self.AIR_ATTACK = AirAttack(self)
        self.SIT_ATTACK = SitAttack(self)
        self.GUARD = Guard(self)
        self.GET_HIT = GetHit(self)
        self.COMBO_ATTACK = ComboAttack(self)

        def mk_key_pred(key_const, sdl_type):
            def pred(e):
                return e[0] == 'INPUT' and e[1].type == sdl_type and e[1].key == key_const
            return pred

        def mk_double_detector_any(sdl_type):
            def pred(e):
                if not (e[0] == 'INPUT' and e[1].type == sdl_type and e[1].key in (self.keymap['left'],
                                                                                   self.keymap['right'])):
                    return False
                if sdl_type == SDL_KEYDOWN:
                    key_const = e[1].key
                    now = get_time()
                    prev_down = self._last_down.get(key_const, 0)
                    prev_up = self._last_up.get(key_const, 0)
                    within_interval = (prev_down != 0) and ((now - prev_down) <= self.double_tap_interval)
                    require_up = getattr(self, 'require_up_between_double', False)
                    had_up_between = (prev_up > prev_down)
                    return within_interval and ((not require_up) or had_up_between)
                return False

            return pred

        def mk_double_fwd_back_combined(sdl_type):
            base = mk_double_detector_any(sdl_type)

            def fwd(e):
                if not base(e):
                    return False
                key_const = e[1].key
                key_dir = 1 if key_const == self.keymap['right'] else -1
                return key_dir == self.face_dir

            def back(e):
                if not base(e):
                    return False
                key_const = e[1].key
                key_dir = 1 if key_const == self.keymap['right'] else -1
                return key_dir != self.face_dir

            return fwd, back

        self.double_fwd, self.double_back = mk_double_fwd_back_combined(SDL_KEYDOWN)

        self.right_down = mk_key_pred(self.keymap['right'], SDL_KEYDOWN)
        self.left_down = mk_key_pred(self.keymap['left'], SDL_KEYDOWN)
        self.right_up = mk_key_pred(self.keymap['right'], SDL_KEYUP)
        self.left_up = mk_key_pred(self.keymap['left'], SDL_KEYUP)
        self.up_down = mk_key_pred(self.keymap['up'], SDL_KEYDOWN)
        self.down_down = mk_key_pred(self.keymap['down'], SDL_KEYDOWN)
        self.down_up = mk_key_pred(self.keymap['down'], SDL_KEYUP)
        self.lp_down = mk_key_pred(self.keymap['lp'], SDL_KEYDOWN)
        self.rp_down = mk_key_pred(self.keymap['rp'], SDL_KEYDOWN)
        self.lk_down = mk_key_pred(self.keymap['lk'], SDL_KEYDOWN)
        self.rk_down = mk_key_pred(self.keymap['rk'], SDL_KEYDOWN)
        self.fwd_down = lambda e: self._is_facing_input(e, SDL_KEYDOWN, 'fwd')
        self.back_down = lambda e: self._is_facing_input(e, SDL_KEYDOWN, 'back')
        self.fwd_up = lambda e: self._is_facing_input(e, SDL_KEYUP, 'fwd')
        self.back_up = lambda e: self._is_facing_input(e, SDL_KEYUP, 'back')
        self.land_moving = lambda e: (e[0] == 'LAND') and (self.dir != 0)

        self.state_machine = StateMachine(
            self.IDLE,{
                self.IDLE:{
                    self.double_fwd: self.RUN,self.double_back: self.BACK_DASH, hitted: self.GET_HIT,
                    self.fwd_down: self.WALK, self.back_down: self.WALK, self.up_down: self.JUMP,self.down_down: self.SIT_DOWN,
                    self.lp_down: self.NORMAL_ATTACK,self.rp_down: self.NORMAL_ATTACK,self.lk_down: self.NORMAL_ATTACK,self.rk_down: self.NORMAL_ATTACK
                    },
                self.WALK:{
                    guard : self.GUARD,
                    self.fwd_up:self.IDLE,self.back_up:self.IDLE,self.up_down:self.MOVE_JUMP,self.down_down:self.SIT_DOWN,
                    self.lp_down: self.NORMAL_ATTACK, self.rp_down: self.NORMAL_ATTACK,self.lk_down: self.NORMAL_ATTACK, self.rk_down: self.NORMAL_ATTACK
                    },
                self.JUMP:{
                    guard: self.GUARD,
                    time_out: self.IDLE, pressing_key:self.WALK, pressing_down:self.SIT_DOWN,
                    self.lp_down: self.AIR_ATTACK, self.rp_down: self.AIR_ATTACK, self.lk_down: self.AIR_ATTACK, self.rk_down: self.AIR_ATTACK
                    },
                self.MOVE_JUMP: {
                    guard:self.GUARD,
                    time_out:self.IDLE, pressing_key:self.WALK, pressing_down:self.SIT_DOWN,
                    self.lp_down: self.AIR_ATTACK, self.rp_down: self.AIR_ATTACK, self.lk_down: self.AIR_ATTACK, self.rk_down: self.AIR_ATTACK
                },
                self.RUN:{
                    self.fwd_up:self.IDLE,self.back_up:self.IDLE,self.up_down:self.RUN_JUMP,
                    self.lp_down: self.NORMAL_ATTACK, self.rp_down: self.NORMAL_ATTACK, self.lk_down: self.NORMAL_ATTACK, self.rk_down: self.NORMAL_ATTACK
                },
                self.RUN_JUMP:{
                    guard: self.GUARD,
                    time_out:self.IDLE,pressing_key:self.RUN, pressing_down:self.SIT_DOWN,
                    self.lp_down: self.AIR_ATTACK, self.rp_down: self.AIR_ATTACK, self.lk_down: self.AIR_ATTACK, self.rk_down: self.AIR_ATTACK
                },
                self.BACK_DASH:{
                    time_out:self.IDLE,pressing_key:self.WALK,pressing_down:self.SIT_DOWN
                },
                self.SIT_DOWN:{
                    guard : self.GUARD,
                    self.down_up: self.SIT_UP,
                    self.lp_down: self.SIT_ATTACK, self.rp_down: self.SIT_ATTACK, self.lk_down: self.SIT_ATTACK, self.rk_down: self.SIT_ATTACK
                    },
                self.SIT_UP:{
                    time_out: self.IDLE,self.down_down:self.SIT_DOWN,self.fwd_down:self.WALK,self.back_down:self.WALK,self.up_down:self.JUMP
                },
                self.NORMAL_ATTACK:{
                    time_out:self.IDLE, self.can_combo: self.COMBO_ATTACK
                },
                self.AIR_ATTACK:{
                    time_out:self.JUMP, land : self.IDLE, self.land_moving: self.WALK,
                },
                self.SIT_ATTACK:{
                    self.time_out_and_down: self.SIT_DOWN,  # 애니 끝났고 아래키 눌러져 있으면 SIT_DOWN
                    self.time_out_and_not_down: self.SIT_UP,  # 애니 끝났고 아래키 놓여있으면 IDLE
                },
                self.GUARD:{
                    time_out:self.JUMP ,pressing_key:self.WALK, pressing_down:self.SIT_DOWN,
                },
                self.GET_HIT:{
                    time_out:self.IDLE, hitted:self.GET_HIT
                },
                self.COMBO_ATTACK:{
                    time_out:self.IDLE, self.can_combo: self.COMBO_ATTACK
                }
            }
        )

    def update(self):
        #self.xPos = clamp(50, self.xPos, common.palace_map.cw - 1 - 50)
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        sx = self.xPos - common.palace_map.window_left - 50 - 1
        #self.font.draw(self.xPos - 60, self.yPos + 150, f'(Time: {get_time():.2f}, Dir : {self.dir}, is_hitted : {self.is_hitted})', (255, 255, 0))
        #self.font.draw(self.xPos - 60, self.yPos + 150, f'(is_hitted : {self.is_hitted}, combo_count : {self.combo_count})', (255, 255, 0))
        #self.font.draw(self.xPos - 60, self.yPos + 150,f'(combo_count : {self.combo_count})', (255, 255, 0))
        self.font.draw(sx - 60, self.yPos + 150, f'(hp, atk : {self.hp, self.atk})', (255, 255, 0))
    def handle_event(self, event):
        # 키 입력 처리 및 마지막 up/down 시각 기록
        if event.type == SDL_KEYDOWN:
            if event.key in (self.keymap['left'], self.keymap['right']):
                key_dir = 1 if event.key == self.keymap['right'] else -1
                if key_dir == self.face_dir:
                    self.fwd_pressed = True
                else:
                    self.back_pressed = True

            if event.key == SDLK_1:
                self.face_dir *= -1
            if event.key == self.keymap['down']:
                self.down_pressed = True
            if event.key == self.keymap['rk']:
                self.rk_pressed = True

            # 상태머신에 INPUT 이벤트 먼저 전달
            self.state_machine.handle_state_event(('INPUT', event))


            # 마지막 다운 시각 갱신 (좌/우)
            if event.key in (self.keymap['left'], self.keymap['right'], self.keymap['rk']):
                    self._last_down[event.key] = get_time()
        elif event.type == SDL_KEYUP:
            if event.key in (self.keymap['left'], self.keymap['right']):
                key_dir = 1 if event.key == self.keymap['right'] else -1
                if key_dir == self.face_dir:
                    self.fwd_pressed = False
                else:
                    self.back_pressed = False
                    # 마지막 업 시각 갱신 (좌/우)
                    self._last_up[event.key] = get_time()


            if event.key == self.keymap['down']:
                self.down_pressed = False
                # 업 시각 기록 (아래키)
                self._last_up[event.key] = get_time()
            if event.key == self.keymap['rk']:
                self.rk_pressed = False
                self._last_up[event.key] = get_time()
            # KEYUP는 INPUT 이벤트로 전달
            self.state_machine.handle_state_event(('INPUT', event))

    def _is_facing_input(self, e, sdl_type, param):
        if self.face_dir ==1:
            return e[0] == 'INPUT' and e[1].type == sdl_type and (e[1].key == self.keymap['right'] if param == 'fwd' else e[1].key == self.keymap['left'])
        else:
            return e[0] == 'INPUT' and e[1].type == sdl_type and (e[1].key == self.keymap['left'] if param == 'fwd' else e[1].key == self.keymap['right'])

    def register_hitbox(self,hb_kind:str,frame_num):
        ox,oy,w,h = self.image.frame_list[frame_num]
        hitbox = HitBox(self, hb_kind, (self.xPos, self.yPos, w, h))
        self.manager.register_hitbox(hitbox)
        return hitbox

    def update_hitbox(self, hitbox:HitBox,frame_num):
        ox, oy, w, h = self.image.frame_list[frame_num]
        sx = self.xPos - common.palace_map.window_left - 50
        offset_width = 20
        if self.face_dir == 1:
            hitbox.update((sx - w, self.yPos - h, CHARACTER_WIDTH_SCALE * w - offset_width, CHARACTER_HEIGHT_SCALE*h))
        else:
            hitbox.update((sx - w + offset_width, self.yPos - h, CHARACTER_WIDTH_SCALE * w - offset_width, CHARACTER_HEIGHT_SCALE*h))