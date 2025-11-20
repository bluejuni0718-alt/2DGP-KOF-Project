from pico2d import *

import game_framework
from frame import *
from state_machine import *
from character_frame import *
from character_frame import CHARACTER_WIDTH_SCALE, CHARACTER_HEIGHT_SCALE

def _register_hitboxes_from_info(character, manager, info, frame_idx, name_prefix='attack'):
    if not manager or not info:
        return
    hitboxes = info.get('hitboxes', [])
    if not hitboxes:
        return
    idx = max(0, min(int(frame_idx), len(hitboxes) - 1))
    hb_defs = hitboxes[idx] if idx < len(hitboxes) else None
    if not hb_defs:
        return

    img = getattr(character, 'image', None)
    sx = float(getattr(character, 'scale_x', getattr(character, 'scale', CHARACTER_WIDTH_SCALE)))
    sy = float(getattr(character, 'scale_y', getattr(character, 'scale', CHARACTER_HEIGHT_SCALE)))
    delx = float(getattr(img, 'delXPos', 0.0)) * sx if img is not None else 0.0
    dely = float(getattr(img, 'delYPos', 0.0)) * sy if img is not None else 0.0

    cx = float(getattr(character, 'xPos', 0.0)) + delx
    cy = float(getattr(character, 'yPos', 0.0)) + dely
    face = int(getattr(character, 'face_dir', 1))

    try:
        if not hasattr(character, 'hitbox_ids') or character.hitbox_ids is None:
            character.hitbox_ids = []
    except Exception:
        character.hitbox_ids = []

    for i, hb in enumerate(hb_defs):
        try:
            if isinstance(hb, dict):
                ox = float(hb.get('x', 0.0))
                oy = float(hb.get('y', 0.0))
                w = float(hb.get('w', hb.get('width', 0.0)))
                h = float(hb.get('h', hb.get('height', 0.0)))
                tag = hb.get('tag', None)
                custom_id = hb.get('id', None)
            else:
                try:
                    ox = float(hb[0]); oy = float(hb[1]); w = float(hb[2]); h = float(hb[3])
                    tag = hb[4] if len(hb) > 4 else None
                    custom_id = None
                except Exception:
                    continue

            ox = ox * sx * (1 if face == 1 else -1)
            oy = oy * sy
            w = w * sx
            h = h * sy

            left = cx + ox - (w / 2.0)
            bottom = cy + oy - (h / 2.0)
            right = left + w
            top = bottom + h

            hb_id = custom_id if custom_id else f'{name_prefix}_{i}_{id(character)}'
            try:
                # rect를 bbox로 전달 (left, bottom, right, top)
                manager.register_hitbox(character, hb_id, rect=(left, bottom, right, top), tag=tag)
            except Exception:
                pass

            try:
                character.hitbox_ids.append(hb_id)
            except Exception:
                try:
                    character.hitbox_ids = list(getattr(character, 'hitbox_ids', []))
                    character.hitbox_ids.append(hb_id)
                except Exception:
                    pass
        except Exception:
            continue

def _register_extra_attack_hitboxes(character, manager, kind):
    """normal|sit|air 용 보조 전방/아래 히트박스 등록. manager에 등록하고 character.hitbox_ids에 id 저장"""
    if not manager or character is None:
        return

    img = getattr(character, 'image', None)
    sx = float(getattr(character, 'scale_x', getattr(character, 'scale', CHARACTER_WIDTH_SCALE)))
    sy = float(getattr(character, 'scale_y', getattr(character, 'scale', CHARACTER_HEIGHT_SCALE)))
    delx = float(getattr(img, 'delXPos', 0.0)) * sx if img is not None else 0.0
    dely = float(getattr(img, 'delYPos', 0.0)) * sy if img is not None else 0.0

    cx = float(getattr(character, 'xPos', 0.0)) + delx
    cy = float(getattr(character, 'yPos', 0.0)) + dely
    face = int(getattr(character, 'face_dir', 1))

    fw, fh = character._get_frame_size_from_image()
    scaled_w = float(fw) * sx
    scaled_h = float(fh) * sy

    forward_gap = 8.0 * sx
    down_gap = 4.0 * sy

    def reg(hb_id, rect, tag='attack'):
        try:
            manager.register_hitbox(character, hb_id, rect=rect, tag=tag)
        except Exception:
            try:
                # 등록 실패하면 무시
                pass
            except Exception:
                pass
        try:
            if not hasattr(character, 'hitbox_ids') or character.hitbox_ids is None:
                character.hitbox_ids = []
        except Exception:
            character.hitbox_ids = []
        try:
            character.hitbox_ids.append(hb_id)
        except Exception:
            try:
                character.hitbox_ids = list(getattr(character, 'hitbox_ids', []))
                character.hitbox_ids.append(hb_id)
            except Exception:
                pass

    kind = (kind or '').lower()
    if kind == 'normal':
        w = max(8.0, scaled_w * 0.28)
        h = max(16.0, scaled_h * 0.6)
        cx_off = face * (scaled_w / 2.0 + (w / 2.0) + forward_gap)
        left = cx + cx_off - (w / 2.0)
        bottom = cy #- (h / 4.0)
        reg(f'attack_normal_front_{id(character)}', (left, bottom, w, h), tag='attack')
    elif kind == 'sit':
        w = max(20.0, scaled_w * 1.0)
        h = max(8.0, scaled_h * 0.35)
        cx_off = face * (scaled_w / 2.0 + (w / 2.0) + forward_gap * 0.6)
        cy_off = - (scaled_h * 0.35)
        left = cx + cx_off - (w / 2.0)
        bottom = cy + cy_off - (h / 2.0)
        reg(f'attack_sit_forward_{id(character)}', (left, bottom, w, h), tag='attack')
    elif kind == 'air':
        w1 = max(8.0, scaled_w * 0.25)
        h1 = max(16.0, scaled_h * 1.15)
        cx_off1 = face * (scaled_w / 2.0 + (w1 / 2.0) + forward_gap)
        left1 = cx + cx_off1 - (w1 / 2.0)
        bottom1 = cy - (h1 / 2.0)
        reg(f'attack_air_front_{id(character)}', (left1, bottom1, w1, h1), tag='attack')

        w2 = max(20.0, scaled_w * 1.1)
        h2 = max(8.0, scaled_h * 0.36)
        cx_off2 = 0.0
        cy_off2 = - (scaled_h / 2.0 + (h2 / 2.0) + down_gap)
        left2 = cx + cx_off2 - (w2 / 2.0)
        bottom2 = cy + cy_off2
        reg(f'attack_air_below_{id(character)}', (left2, bottom2, w2, h2), tag='attack')
    else:
        return



PIXEL_PER_METER = 10.0/0.15 #10 픽셀당 30cm로 설정

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

def time_out(e):
    return e[0] == 'TIME_OUT'

def pressing_key(e):
    return e[0] == 'Pressing_Key'

def pressing_down(e):
    return e[0] == 'Pressing_Down'

def land(e):
    return e[0] == 'LAND'

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
        self.character.frame = (self.character.frame + FRAMES_PER_ACTION * ACTION_PER_TIME*game_framework.frame_time) % self.character.image.idle_frames
        pass
    def draw(self):
        self.character.image.draw_idle_by_frame_num(int(self.character.frame), self.character.xPos, self.character.yPos,self.character.face_dir)
        pass

class Walk:
    def __init__(self, character):
        self.character=character
    def enter(self, e):
        self.character.frame = 0
        self.character.jump_frame = 0
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
        pass
    def exit(self,e):
        self.character.dir=0
        pass
    def do(self):
        self.character.frame = (self.character.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % self.character.image.walk_frames
        self.character.xPos +=self.character.dir * WALK_SPEED_PPS * game_framework.frame_time
        pass
    def draw(self):
        self.character.image.draw_by_frame_num(self.character.image.walk_frame_start + int(self.character.frame),self.character.xPos, self.character.yPos,self.character.face_dir)
        pass

class Jump:
    def __init__(self, character):
        self.character = character
        self.gravity = -3000.0
        self.desired_jump_height = 240

    def enter(self, e):
        self.character.frame = self.character.jump_frame
        # 진입 시 기준 바닥은 항상 default_ground_y로 고정
        self.character.ground_y = self.character.default_ground_y
        # 처음 점프일 때만 vy 설정 (TIME_OUT으로 다시 들어올 때 재설정하지 않음)
        if not (e and e[0] == 'TIME_OUT'):
            g_abs = -self.gravity if self.gravity < 0 else self.gravity
            self.character.vy = (2 * g_abs * self.desired_jump_height) ** 0.5
            if self.character.vy < 0:
                self.character.vy = -self.character.vy

    def exit(self, e):
        self.character.jump_frame = self.character.frame
        self.character.dir = 0

    def do(self):
        self.character.frame = (self.character.frame +
                                FRAMES_PER_JUMP_ACTION * JUMP_ACTION_PER_TIME * game_framework.frame_time) \
                               % max(1, getattr(self.character.image, 'jump_frames', 1))
        self.character.vy += self.gravity * game_framework.frame_time
        self.character.yPos += self.character.vy * game_framework.frame_time

        if self.character.yPos <= self.character.ground_y:
            # 착지 시 항상 기본 바닥으로 복원
            self.character.ground_y = self.character.default_ground_y
            self.character.yPos = self.character.default_ground_y
            if self.character.fwd_pressed or self.character.back_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Key', None))
            elif self.character.down_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Down', None))
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        self.character.image.draw_by_frame_num(
            self.character.image.jump_frame_start + int(self.character.frame),
            self.character.xPos, self.character.yPos, self.character.face_dir)

class MoveJump:
    def __init__(self, character):
        self.character = character
        self.gravity = -3000.0
        self.desired_jump_height = 240

    def enter(self, e):
        self.character.frame = self.character.jump_frame
        # 기준 바닥을 기본값으로 고정
        self.character.ground_y = self.character.default_ground_y
        if not (e and e[0] == 'TIME_OUT'):
            g_abs = -self.gravity if self.gravity < 0 else self.gravity
            self.character.vy = (2 * g_abs * self.desired_jump_height) ** 0.5
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

    def exit(self, e):
        self.character.jump_frame = self.character.frame
        def _is_attack_transition(ev):
            if not ev:
                return False
            if ev[0] == 'ATTACK':
                return True
            if ev[0] == 'INPUT' and getattr(ev[1], 'type', None) == SDL_KEYDOWN:
                atk_keys = (
                    self.character.keymap.get('lp'),
                    self.character.keymap.get('rp'),
                    self.character.keymap.get('lk'),
                    self.character.keymap.get('rk'),
                )
                return ev[1].key in atk_keys
            return False

        if not _is_attack_transition(e):
            self.character.dir = 0

    def do(self):
        if self.character.dir == 1:
            self.character.frame = (self.character.frame +
                                    self.character.face_dir * FRAMES_PER_MOVE_JUMP_ACTION * MOVE_JUMP_ACTION_PER_TIME * game_framework.frame_time) \
                                   % max(1, getattr(self.character.image, 'jump_move_frames', 1))
        else:
            self.character.frame = (self.character.frame -
                                    self.character.face_dir * FRAMES_PER_MOVE_JUMP_ACTION * MOVE_JUMP_ACTION_PER_TIME * game_framework.frame_time) \
                                   % max(1, getattr(self.character.image, 'jump_move_frames', 1))

        self.character.vy += self.gravity * game_framework.frame_time
        self.character.yPos += self.character.vy * game_framework.frame_time
        self.character.xPos += self.character.dir * WALK_SPEED_PPS * game_framework.frame_time

        if self.character.yPos <= self.character.ground_y:
            # 착지 시 기본 바닥으로 복원
            self.character.ground_y = self.character.default_ground_y
            self.character.yPos = self.character.default_ground_y
            if self.character.fwd_pressed or self.character.back_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Key', None))
            elif self.character.down_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Down', None))
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        self.character.image.draw_by_frame_num(
            self.character.image.jump_move_motion_list[int(self.character.frame)],
            self.character.xPos, self.character.yPos, self.character.face_dir)

class Run:
    def __init__(self, character):
        self.character=character
    def enter(self, e):
        self.character.anim_tick = 0
        self.character.frame = 0
        self.character.jump_frame = 0
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
        pass
    def exit(self,e):
        self.character.dir = 0
        pass
    def do(self):
        self.character.frame = (self.character.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % self.character.image.run_frames
        self.character.xPos += self.character.dir * RUN_SPEED_PPS * game_framework.frame_time
    def draw(self):
        self.character.image.draw_by_frame_num(self.character.image.run_frame_start + int(self.character.frame),self.character.xPos, self.character.yPos,self.character.face_dir)
        pass

class RunJump:
    def __init__(self, character):
        self.character = character
        self.gravity = -3000.0
        self.desired_jump_height = 240

    def enter(self, e):
        self.character.frame = self.character.jump_frame
        # 기준 바닥 고정
        self.character.ground_y = self.character.default_ground_y
        # 초기 수직속도를 캐릭터 속성으로 설정 (모든 상태가 동일한 vy를 보게 됨)
        g_abs = -self.gravity if self.gravity < 0 else self.gravity
        vy = (2 * g_abs * self.desired_jump_height) ** 0.5
        if vy < 0:
            vy = -vy
        self.character.vy = vy

        # 방향 결정 (기존)
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

    def exit(self, e):
        self.character.jump_frame = self.character.frame

        def _is_attack_transition(ev):
            if not ev:
                return False
            if ev[0] == 'ATTACK':
                return True
            if ev[0] == 'INPUT' and getattr(ev[1], 'type', None) == SDL_KEYDOWN:
                atk_keys = (
                    self.character.keymap.get('lp'),
                    self.character.keymap.get('rp'),
                    self.character.keymap.get('lk'),
                    self.character.keymap.get('rk'),
                )
                return ev[1].key in atk_keys
            return False

        if _is_attack_transition(e):
            # 런에서 점프한 상태에서 공격으로 전환될 때 현재 런 속도를 vx로 보존
            if getattr(self.character, 'dir', 0) != 0:
                self.character.vx = self.character.dir * RUN_SPEED_PPS
        else:
            # 공격이 아닌 전환이면 방향 초기화 및 vx 삭제
            self.character.dir = 0
            if hasattr(self.character, 'vx'):
                self.character.vx = 0.0

    def do(self):
        dt = game_framework.frame_time
        # 프레임 진행 (기존 로직 유지)
        if self.character.dir == 1:
            self.character.frame = (self.character.frame +
                                    self.character.face_dir * FRAMES_PER_MOVE_JUMP_ACTION * MOVE_JUMP_ACTION_PER_TIME * dt) \
                                   % max(1, getattr(self.character.image, 'jump_move_frames', 1))
        else:
            self.character.frame = (self.character.frame -
                                    self.character.face_dir * FRAMES_PER_MOVE_JUMP_ACTION * MOVE_JUMP_ACTION_PER_TIME * dt) \
                                   % max(1, getattr(self.character.image, 'jump_move_frames', 1))

        # vertical: 항상 character.vy 사용
        self.character.vy += self.gravity * dt
        self.character.yPos += self.character.vy * dt

        # horizontal
        self.character.xPos += self.character.dir * RUN_SPEED_PPS * dt

        if self.character.yPos <= self.character.ground_y:
            # 착지 시 기본 바닥으로 복원
            self.character.ground_y = self.character.default_ground_y
            self.character.yPos = self.character.default_ground_y
            if self.character.fwd_pressed or self.character.back_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Key', None))
            elif self.character.down_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Down', None))
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        self.character.image.draw_by_frame_num(self.character.image.jump_move_motion_list[int(self.character.frame)],
                                               self.character.xPos, self.character.yPos, self.character.face_dir)

class BackDash:
    def __init__(self, character):
        self.character = character
        self.vy = 0.0
        self.gravity = -1500.0
        self.desired_jump_height = 10

    def enter(self, e):
        self.character.ground_y = self.character.yPos
        g_abs = -self.gravity if self.gravity < 0 else self.gravity
        self.vy = (2 * g_abs * self.desired_jump_height) ** 0.5
        if self.vy < 0:
            self.vy = -self.vy
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
    def exit(self, e):
        self.character.dir = 0
        pass

    def do(self):
        self.vy += self.gravity * game_framework.frame_time
        self.character.yPos += self.vy * game_framework.frame_time
        self.character.xPos += self.character.dir * BACK_DASH_SPEED_PPS * game_framework.frame_time

        if self.character.yPos <= self.character.ground_y:
            self.character.yPos = self.character.ground_y
            if self.character.fwd_pressed or self.character.back_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Key', None))
            elif self.character.down_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Down', None))
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        self.character.image.draw_by_frame_num(self.character.image.back_dash_frame_start,
                                               self.character.xPos, self.character.yPos, self.character.face_dir)

class SitDown:
    def __init__(self, character):
        self.character = character
        # 내부 sticky 상태: SitAttack에서 돌아와서 마지막 프레임을 유지해야 할 때 True
        self.fix_last_frame = False

    def enter(self, e):
        # SitAttack에서 돌아올 때 마지막 프레임 고정
        if self.character.keep_sit_down_last_frame:
            self.character.frame = 2
            self.character.keep_sit_down_last_frame = False
            self.fix_last_frame = True
        else:
            self.character.frame = 0
            self.fix_last_frame = False
    def exit(self, e):
        self.character.frame = 0
        self.fix_last_frame = False

    def do(self):
        # sticky이면 프레임을 증가시키지 않고 마지막 프레임에 고정
        if self.fix_last_frame:
            self.character.frame=2
        else:
            if self.character.frame <2:
                self.character.frame = (self.character.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % self.character.image.sit_down_frames

    def draw(self):
        self.character.image.draw_by_frame_num(
            self.character.image.sit_down_frame_start + int(self.character.frame),
            self.character.xPos,
            self.character.yPos - 6 * int(self.character.frame),
            self.character.face_dir)

class SitUp:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = max(0.0, getattr(self.character.image, 'sit_down_frames', 1) - 1.0)
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
        self.character.image.draw_by_frame_num(self.character.image.sit_down_frame_start + int(self.character.frame), self.character.xPos, self.character.yPos - 6 * int(self.character.frame),self.character.face_dir)
        pass

class NormalAttack:
    def __init__(self, character):
        self.character = character
        self.attack_key = None   # 'rp'|'lp'|'rk'|'lk'
        self.combo_accept_last_frames = 2  # 마지막 N프레임에서 콤보 허용

    def enter(self, e):
        self.character.frame = 0.0
        self.attack_key = None
        if e and e[0] == 'ATTACK':
            self.attack_key = e[1]
        elif e and e[0] == 'INPUT':
            ev = e[1]
            for k in ('rp', 'lp', 'rk', 'lk'):
                if ev.key == self.character.keymap.get(k):
                    self.attack_key = k
                    break
        if not self.attack_key:
            self.attack_key = 'rp'
        # 엔터 시 오래된 버퍼는 제거
        now = get_time()
        self.character.attack_buffer = [(k, t) for (k, t) in self.character.attack_buffer if now - t <= self.character.attack_buffer_window]
        try:
            self.character.is_attacking = True
        except Exception:
            pass
    def exit(self, e):
        self.character.frame = 0.0
        self.attack_key = None
        # 엔터/종료 시 버퍼 정리(원하면)
        self.character.attack_buffer.clear()
        try:
            self.character.is_attacking = False
        except Exception:
            pass

    def _consume_buffered_attack(self):
        now = get_time()
        for i, (k, t) in enumerate(self.character.attack_buffer):
            if now - t <= self.character.attack_buffer_window:
                # 간단히 아무 공격키나 허용하거나, 특정 체인만 허용하도록 검사 가능
                return self.character.attack_buffer.pop(i)  # (k, t)
        return None

    def do(self):
        self.character.frame += FRAMES_PER_ATTACK_ACTION * ATTACK_ACTION_PER_TIME * game_framework.frame_time
        frames = getattr(self.character.image, 'normal_attacks', {}).get(self.attack_key, {}).get('frames', [])
        frame_count = len(frames)
        if frame_count == 0:
            self.character.state_machine.handle_state_event(('TIME_OUT', None))
            return

        # 콤보 허용 구간 검사: 마지막 N프레임 이내일 때만 체인 허용
        current_idx = min(int(self.character.frame), frame_count - 1)
        accept_from = max(0, frame_count - self.combo_accept_last_frames)
        if current_idx >= accept_from:
            consumed = self._consume_buffered_attack()
            if consumed:
                next_attack_key, _ = consumed
                # 체인 로직: 다음 공격키로 교체하고 애니메이션 리셋
                self.attack_key = next_attack_key
                self.character.frame = 0.0
                return

        if int(self.character.frame) >= frame_count:
            self.character.state_machine.handle_state_event(('TIME_OUT', None))

    def register_hitboxes(self, manager):
        info = getattr(self.character.image, 'normal_attacks', {}).get(self.attack_key or 'rp', {})
        _register_hitboxes_from_info(self.character, manager, info, self.character.frame,
                                     name_prefix=f'normal_{self.attack_key or "rp"}')
        # 보조 전방/아래 히트박스 등록
        _register_extra_attack_hitboxes(self.character, manager, 'normal')

    def draw(self):
        frames = getattr(self.character.image, 'normal_attacks', {}).get(self.attack_key, {}).get('frames', [])
        if not frames:
            return
        idx = min(int(self.character.frame), len(frames) - 1)
        self.character.image.draw_normal_attack(self.attack_key, idx,
                                                self.character.xPos, self.character.yPos, self.character.face_dir)

class AirAttack:
    def __init__(self, character):
        self.character = character
        self.attack_key = None
        self.combo_accept_last_frames = 2
        self.gravity = -3000.0

    def enter(self, e):
        self.character.frame = 0.0
        self.attack_key = None
        if e and e[0] == 'ATTACK':
            self.attack_key = e[1]
        elif e and e[0] == 'INPUT':
            ev = e[1]
            try:
                for k in ('rp', 'lp', 'rk', 'lk'):
                    if ev.key == self.character.keymap.get(k):
                        self.attack_key = k
                        break
            except Exception:
                pass
        if not self.attack_key:
            self.attack_key = 'rp'
        now = get_time()
        try:
            self.character.attack_buffer = [(k, t) for (k, t) in self.character.attack_buffer if
                                            now - t <= self.character.attack_buffer_window]
        except Exception:
            self.character.attack_buffer = []
        try:
            self.character.is_attacking = True
        except Exception:
            pass

    def exit(self, e):
        self.character.frame = 0.0
        self.attack_key = None
        try:
            self.character.attack_buffer.clear()
        except Exception:
            self.character.attack_buffer = []
        # 점프공격에서 보존한 vx 초기화
        try:
            if hasattr(self.character, 'vx'):
                self.character.vx = 0.0
        except Exception:
            pass
        try:
            self.character.is_attacking = False
        except Exception:
            pass

    def _consume_buffered_attack(self):
        now = get_time()
        for i, (k, t) in enumerate(self.character.attack_buffer):
            if now - t <= self.character.attack_buffer_window:
                return self.character.attack_buffer.pop(i)
        return None

    def do(self):
        dt = game_framework.frame_time
        # 애니 진행 및 중력 처리
        self.character.frame += FRAMES_PER_ATTACK_ACTION * ATTACK_ACTION_PER_TIME * dt
        self.character.vy += self.gravity * dt
        self.character.yPos += self.character.vy * dt

        # 착지 처리
        if self.character.yPos <= self.character.ground_y:
            self.character.ground_y = self.character.default_ground_y
            self.character.yPos = self.character.default_ground_y
            # 착지 시 vx 초기화
            if hasattr(self.character, 'vx'):
                self.character.vx = 0.0
            self.character.state_machine.handle_state_event(('LAND', None))
            return

        vx = getattr(self.character, 'vx', 0.0)
        if vx and abs(vx) > 0.0:
            self.character.xPos += vx * dt
        elif getattr(self.character, 'dir', 0) != 0:
            # 런에서 온 경우에는 RunJump.exit에서 vx를 세팅했으므로 여기서는 보통 WALK 속도로 처리
            self.character.xPos += self.character.dir * WALK_SPEED_PPS * dt

        # dir 기반으로 프레임셋 선택
        if getattr(self.character, 'dir', 0) != 0:
            info = getattr(self.character.image, 'move_jump_attacks', {}).get(self.attack_key, {})
        else:
            info = getattr(self.character.image, 'jump_attacks', {}).get(self.attack_key, {})

        frames = info.get('frames', [])
        frame_count = len(frames)
        if frame_count == 0:
            self.character.state_machine.handle_state_event(('TIME_OUT', None))
            return

        current_idx = min(int(self.character.frame), frame_count - 1)
        accept_from = max(0, frame_count - self.combo_accept_last_frames)
        if current_idx >= accept_from:
            consumed = self._consume_buffered_attack()
            if consumed:
                next_attack_key, _ = consumed
                self.attack_key = next_attack_key
                self.character.frame = 0.0
                return

        if int(self.character.frame) >= frame_count:
            self.character.state_machine.handle_state_event(('TIME_OUT', None))

    def register_hitboxes(self, manager):
        info = getattr(self.character.image, 'air_attacks', {}).get(self.attack_key or 'rp', {})
        _register_hitboxes_from_info(self.character, manager, info, self.character.frame, name_prefix='air_attack')
        # 보조 전방/아래 히트박스 등록
        _register_extra_attack_hitboxes(self.character, manager, 'air')

    def draw(self):
        # 오직 dir != 0 일 때만 move_jump_attacks 사용, 아니면 jump_attacks 사용
        if getattr(self.character, 'dir', 0) != 0:
            info = getattr(self.character.image, 'move_jump_attacks', {}).get(self.attack_key, {})
            frames = info.get('frames', []) if info else []
            if frames:
                idx = max(0, min(int(self.character.frame), len(frames) - 1))
                frame_num = frames[idx]
                self.character.image.draw_by_frame_num(frame_num, self.character.xPos, self.character.yPos, self.character.face_dir)
                return

        frames = getattr(self.character.image, 'jump_attacks', {}).get(self.attack_key, {}).get('frames', [])
        if not frames:
            return
        idx = max(0, min(int(self.character.frame), len(frames) - 1))
        self.character.image.draw_jump_attack(self.attack_key, idx, self.character.xPos, self.character.yPos, self.character.face_dir)

class SitAttack:
    def __init__(self, character):
        self.character = character
        self.attack_key = None
        self.combo_accept_last_frames = 2

    def enter(self, e):
        self.character.frame = 0.0
        self.attack_key = None
        if e and e[0] == 'ATTACK':
            self.attack_key = e[1]
        elif e and e[0] == 'INPUT':
            ev = e[1]
            try:
                for k in ('rp', 'lp', 'rk', 'lk'):
                    if ev.key == self.character.keymap.get(k):
                        self.attack_key = k
                        break
            except Exception:
                pass
        if not self.attack_key:
            self.attack_key = 'rp'
        now = get_time()
        try:
            self.character.attack_buffer = [(k, t) for (k, t) in self.character.attack_buffer if
                                            now - t <= self.character.attack_buffer_window]
        except Exception:
            self.character.attack_buffer = []
        try:
            self.character.is_attacking = True
        except Exception:
            pass

    def exit(self, e):
        self.character.frame = 0.0
        self.attack_key = None
        try:
            self.character.attack_buffer.clear()
        except Exception:
            self.character.attack_buffer = []
        # SitDown으로 복귀 시 마지막 프레임 유지 요청 (있으면 SitDown에서 처리됨)
        if self.character.down_pressed:
            self.character.keep_sit_down_last_frame = True
        else:
            self.character.keep_sit_down_last_frame = False

    def _consume_buffered_attack(self):
        now = get_time()
        for i, (k, t) in enumerate(self.character.attack_buffer):
            if now - t <= self.character.attack_buffer_window:
                return self.character.attack_buffer.pop(i)
        return None

    def do(self):
        self.character.frame += FRAMES_PER_ATTACK_ACTION * ATTACK_ACTION_PER_TIME * game_framework.frame_time
        info = getattr(self.character.image, 'sit_attacks', {}).get(self.attack_key, {})
        frames = info.get('frames', [])
        frame_count = len(frames)
        if frame_count == 0:
            self.character.state_machine.handle_state_event(('TIME_OUT', None))
            return

        current_idx = min(int(self.character.frame), frame_count - 1)
        accept_from = max(0, frame_count - self.combo_accept_last_frames)
        if current_idx >= accept_from:
            consumed = self._consume_buffered_attack()
            if consumed:
                next_attack_key, _ = consumed
                self.attack_key = next_attack_key
                self.character.frame = 0.0
                return

        if int(self.character.frame) >= frame_count:
            self.character.state_machine.handle_state_event(('TIME_OUT', None))

    def register_hitboxes(self, manager):
        info = getattr(self.character.image, 'sit_attacks', {}).get(self.attack_key or 'rp', {})
        _register_hitboxes_from_info(self.character, manager, info, self.character.frame, name_prefix='sit_attack')
        # 보조 전방 히트박스 등록
        _register_extra_attack_hitboxes(self.character, manager, 'sit')

    def draw(self):
        info = getattr(self.character.image, 'sit_attacks', {}).get(self.attack_key, {})
        frames = info.get('frames', [])
        offsets = info.get('offsets', [(0, 0)] * len(frames))
        if not frames:
            return
        idx = max(0, min(int(self.character.frame), len(frames) - 1))
        frame_num = frames[idx]
        ox, oy = offsets[idx] if idx < len(offsets) else (0, 0)
        ox = ox * -self.character.face_dir
        self.character.image.delXPos = ox
        self.character.image.delYPos = oy
        self.character.image.draw_by_frame_num(frame_num, self.character.xPos, self.character.yPos, self.character.face_dir)

class Guard:
    def __init__(self, character):
        self.character = character
        self.frame_count = max(1, getattr(self.character.image, 'guard_stand_frames', 1))

    def enter(self, e):
        self.character.frame = 0.0
        # 가드 진입 시 공격 플래그 해제하고 가드 상태 설정
        self.character.is_attacking = False
        self.character.guard_stance = True

    def exit(self, e):
        self.character.guard_stance = False
        self.character.frame = 0.0

    def do(self):
        # 가드 애니 진행
        dt = game_framework.frame_time
        self.frame_count = max(1, getattr(self.character.image, 'guard_stand_frames', 1))
        self.character.frame = (self.character.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * dt) % self.frame_count

        # 가드 유지 조건 실패 시 상태 전환
        # (예: 지면이 아니거나 백 버튼이 해제되었거나 공격중인 경우)
        can_guard = getattr(self.character, '_can_guard', lambda: False)()
        if not can_guard or not self.character.back_pressed:
            # TIME_OUT으로 빠져나가도록 함 (상황에 맞게 다른 이벤트로 변경 가능)
            try:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))
            except Exception:
                pass

    def draw(self):
        # draw_guard를 활용하도록 통합
        if hasattr(self.character, 'draw_guard'):
            self.character.draw_guard()
        else:
            # 최소 페일백: 기본 상태머신 그리기
            self.character.state_machine.draw()

class Character:
    def __init__(self, image_data,keymap=None, manager=None, x = 400, y = 120):
        default = {'left': SDLK_a, 'right': SDLK_d, 'up': SDLK_w,'down':SDLK_s,'lp':SDLK_f,'rp':SDLK_g,'rk':SDLK_b,'lk':SDLK_c}
        self.font = load_font('ENCR10B.TTF', 16)
        self.keymap = default if keymap is None else {**default, **keymap}
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

        self._last_down = {}  # key_const -> 마지막 다운 시각
        self._last_up = {}  # key_const -> 마지막 업 시각

        self.manager = manager
        self.hitbox_ids = []

        self.fwd_pressed = False
        self.back_pressed = False
        self.down_pressed = False

        self.keep_sit_down_last_frame = False
        self._deferred_facing = None  # <-- 추가
        # 외부 코드에서 self._keep_sit_down_last_frame와 self.keep_sit_down_last_frame 둘다 참조할 수 있게 동기화
        self.time_out_and_down = lambda e: (e[0] == 'TIME_OUT') and self.down_pressed
        self.time_out_and_not_down = lambda e: (e[0] == 'TIME_OUT') and (not self.down_pressed)

        self.attack_buffer = []  # list of (attack_key_str, timestamp)
        self.attack_buffer_window = 0.35  # 버퍼 유효 시간(초)

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
                    self.double_fwd: self.RUN,self.double_back: self.BACK_DASH,
                    self.fwd_down: self.WALK,self.back_down: self.WALK,self.up_down: self.JUMP,self.down_down: self.SIT_DOWN,
                    self.lp_down: self.NORMAL_ATTACK,self.rp_down: self.NORMAL_ATTACK,self.lk_down: self.NORMAL_ATTACK,self.rk_down: self.NORMAL_ATTACK
                    },
                self.WALK:{
                    self.fwd_up:self.IDLE,self.back_up:self.IDLE,self.up_down:self.MOVE_JUMP,self.down_down:self.SIT_DOWN,
                    self.lp_down: self.NORMAL_ATTACK, self.rp_down: self.NORMAL_ATTACK,self.lk_down: self.NORMAL_ATTACK, self.rk_down: self.NORMAL_ATTACK
                    },
                self.JUMP:{
                    time_out: self.IDLE, pressing_key:self.WALK, pressing_down:self.SIT_DOWN,
                    self.lp_down: self.AIR_ATTACK, self.rp_down: self.AIR_ATTACK, self.lk_down: self.AIR_ATTACK, self.rk_down: self.AIR_ATTACK
                    },
                self.MOVE_JUMP: {
                    time_out:self.IDLE, pressing_key:self.WALK, pressing_down:self.SIT_DOWN,
                    self.lp_down: self.AIR_ATTACK, self.rp_down: self.AIR_ATTACK, self.lk_down: self.AIR_ATTACK, self.rk_down: self.AIR_ATTACK
                },
                self.RUN:{
                    self.fwd_up:self.IDLE,self.back_up:self.IDLE,self.up_down:self.RUN_JUMP,
                    self.lp_down: self.NORMAL_ATTACK, self.rp_down: self.NORMAL_ATTACK, self.lk_down: self.NORMAL_ATTACK, self.rk_down: self.NORMAL_ATTACK
                },
                self.RUN_JUMP:{
                    time_out:self.IDLE,pressing_key:self.RUN, pressing_down:self.SIT_DOWN,
                    self.lp_down: self.AIR_ATTACK, self.rp_down: self.AIR_ATTACK, self.lk_down: self.AIR_ATTACK, self.rk_down: self.AIR_ATTACK
                },
                self.BACK_DASH:{
                    time_out:self.IDLE,pressing_key:self.WALK,pressing_down:self.SIT_DOWN
                },
                self.SIT_DOWN:{
                    self.down_up: self.SIT_UP,
                    self.lp_down: self.SIT_ATTACK, self.rp_down: self.SIT_ATTACK, self.lk_down: self.SIT_ATTACK, self.rk_down: self.SIT_ATTACK
                    },
                self.SIT_UP:{
                    time_out: self.IDLE,self.down_down:self.SIT_DOWN,self.fwd_down:self.WALK,self.back_down:self.WALK,self.up_down:self.JUMP
                },
                self.NORMAL_ATTACK:{
                    time_out:self.IDLE,
                },
                self.AIR_ATTACK:{
                    time_out:self.JUMP, land : self.IDLE, self.land_moving: self.WALK,
                },
                self.SIT_ATTACK:{
                    self.time_out_and_down: self.SIT_DOWN,  # 애니 끝났고 아래키 눌러져 있으면 SIT_DOWN
                    self.time_out_and_not_down: self.SIT_UP,  # 애니 끝났고 아래키 놓여있으면 IDLE
                }

            }
        )

    def update(self):
        self.frame_index = int(self.frame) if hasattr(self, 'frame') else 0
        self.state_machine.update()
    def draw(self):
        self.state_machine.draw()
        self.font.draw(self.xPos - 60, self.yPos + 150, f'(Time: {get_time():.2f}, Dir : {self.dir})', (255, 255, 0))

    def _get_frame_size_from_image(self) -> tuple:
        img = getattr(self, 'image', None)
        if img is None:
            return (0.0, 0.0)
        idx = int(self.frame) if hasattr(self, 'frame') else 0

        # 1) owner 이미지의 frame_list 사용 (튜플/리스트로 fx,fy,fw,fh)
        fl = getattr(img, 'frame_list', None)
        if fl is not None and isinstance(fl, (list, tuple)) and 0 <= idx < len(fl):
            f = fl[idx]
            if isinstance(f, (list, tuple)) and len(f) >= 4:
                return (float(f[2]), float(f[3]))
            # 객체형 프레임
            w = getattr(f, 'w', None) or getattr(f, 'width', None)
            h = getattr(f, 'h', None) or getattr(f, 'height', None)
            if w is not None and h is not None:
                return (float(w), float(h))

        # 2) 이미지 자체에 프레임 크기 속성(w,h,width,height) 존재하면 사용
        w = getattr(img, 'w', None) or getattr(img, 'width', None) or getattr(img, 'frame_width', None)
        h = getattr(img, 'h', None) or getattr(img, 'height', None) or getattr(img, 'frame_height', None)
        if w is not None and h is not None:
            return (float(w), float(h))

        # 3) fallback: 임의 기본값
        return (32.0, 64.0)

    # 히트박스 등록: self.hitbox_ids 를 순회하여 각 히트박스 등록
    def register_hitboxes(self):
        """매 프레임: 이전 히트박스 제거 -> body를 프레임 크기 기준으로 rect=(left,bottom,width,height) 형태(공격 히트박스와 동일 메커니즘)로 등록 -> 상태의 공격 히트박스 호출"""
        if not getattr(self, 'manager', None):
            return
        mgr = self.manager

        # 이전에 등록한 히트박스 제거
        old_ids = getattr(self, 'hitbox_ids', []) or []
        for hid in list(old_ids):
            try:
                if hasattr(mgr, 'unregister_hitbox'):
                    mgr.unregister_hitbox(self, hid)
            except Exception:
                pass
        self.hitbox_ids = []

        # 항상 body 히트박스: 프레임 크기 기준 (공격 히트박스와 같은 rect 포맷: left, bottom, width, height)
        try:
            img = getattr(self, 'image', None)
            fw, fh = self._get_frame_size_from_image()
            sx = float(getattr(self, 'scale_x', getattr(self, 'scale', CHARACTER_WIDTH_SCALE)))
            sy = float(getattr(self, 'scale_y', getattr(self, 'scale', CHARACTER_HEIGHT_SCALE)))
            delx = float(getattr(img, 'delXPos', 0.0)) * sx if img is not None else 0.0
            dely = float(getattr(img, 'delYPos', 0.0)) * sy if img is not None else 0.0

            cx = float(getattr(self, 'xPos', 0.0)) + delx
            cy = float(getattr(self, 'yPos', 0.0)) + dely

            w = fw * sx
            h = fh * sy
            left = cx - (w / 2.0)
            bottom = cy - (h / 2.0)

            hb_id = f'body_{id(self)}'
            registered = False

            # 1) 기본 시그니처: register_hitbox(owner, id, rect=..., tag=...)
            try:
                if hasattr(mgr, 'register_hitbox'):
                    mgr.register_hitbox(self, hb_id, rect=(left, bottom, w, h), tag='body')
                    registered = True
            except Exception:
                registered = False

            # 2) fallback: register_hitbox(id, owner, rect=..., tag=...)
            if not registered:
                try:
                    mgr.register_hitbox(hb_id, self, rect=(left, bottom, w, h), tag='body')
                    registered = True
                except Exception:
                    registered = False

            # 3) 마지막 fallback: 레거시 형태 (left, bottom, width, height) 개별 인수
            if not registered:
                try:
                    mgr.register_hitbox(self, hb_id, left, bottom, w, h, 'body')
                    registered = True
                except Exception:
                    registered = False

            if registered:
                try:
                    self.hitbox_ids.append(hb_id)
                except Exception:
                    self.hitbox_ids = [hb_id]
        except Exception:
            pass

        # 상태 객체의 공격/특수 히트박스 등록(공격 히트박스 로직은 변경하지 않음)
        state_obj = None
        for attr in ('cur_state', 'current_state', 'state', 'cur'):
            try:
                sm = getattr(self, 'state_machine', None)
                state_obj = getattr(sm, attr, None) if sm is not None else None
            except Exception:
                state_obj = None
            if state_obj is not None:
                break

        if state_obj is not None and hasattr(state_obj, 'register_hitboxes'):
            try:
                state_obj.register_hitboxes(self.manager)
            except Exception:
                try:
                    state_obj.register_hitboxes(self, self.manager)
                except Exception:
                    pass

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

            # 상태머신에 INPUT 이벤트 먼저 전달
            self.state_machine.handle_state_event(('INPUT', event))

            # 공격키면 명시적 ATTACK 이벤트도 발행
            atk = None
            for k in ('lp', 'rp', 'lk', 'rk'):
                if event.key == self.keymap.get(k):
                    atk = k
                    break
            if atk:
                self.state_machine.handle_state_event(('ATTACK', atk))

            # 마지막 다운 시각 갱신 (좌/우)
            if event.key in (self.keymap['left'], self.keymap['right']):
                try:
                    self._last_down[event.key] = get_time()
                except Exception:
                    pass

        elif event.type == SDL_KEYUP:
            if event.key in (self.keymap['left'], self.keymap['right']):
                key_dir = 1 if event.key == self.keymap['right'] else -1
                if key_dir == self.face_dir:
                    self.fwd_pressed = False
                else:
                    self.back_pressed = False
                # 마지막 업 시각 갱신 (좌/우)
                try:
                    self._last_up[event.key] = get_time()
                except Exception:
                    pass

            if event.key == self.keymap['down']:
                self.down_pressed = False
                # 업 시각 기록 (아래키)
                try:
                    self._last_up[event.key] = get_time()
                except Exception:
                    pass

            # KEYUP는 INPUT 이벤트로 전달
            self.state_machine.handle_state_event(('INPUT', event))

    def _is_facing_input(self, e, sdl_type, param):
        # 파라미터 이름을 명확히 하고 사용
        if not (e[0] == 'INPUT' and e[1].type == sdl_type and e[1].key in (self.keymap['left'], self.keymap['right'])):
            return False
        key_const = e[1].key
        key_dir = 1 if key_const == self.keymap['right'] else -1
        return (key_dir == self.face_dir) if param == 'fwd' else (key_dir != self.face_dir)

