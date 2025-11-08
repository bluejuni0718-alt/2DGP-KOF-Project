from pico2d import *

import game_framework
from frame import *
from state_machine import *
from character_frame import *

PIXEL_PER_METER = 10.0/0.3 #10 픽셀당 30cm로 설정

RUN_SPEED_KMPH = 20.0 #시속 20km로 설정
RUN_SPEED_MPS = (RUN_SPEED_KMPH * 1000.0 / 3600.0) #초속미터 환산
RUN_SPEED_PPS = (RUN_SPEED_MPS*PIXEL_PER_METER) #초속 픽셀로 환산

WALK_SPEED_KMPH = 5
WALK_SPEED_MPS = (WALK_SPEED_KMPH * 1000.0 / 3600.0)
WALK_SPEED_PPS = (WALK_SPEED_MPS * PIXEL_PER_METER)

JUMP_SPEED_KMPH = 50
JUMP_SPEED_MPS = (JUMP_SPEED_KMPH * 1000.0 / 3600.0)
JUMP_SPEED_PPS = (JUMP_SPEED_MPS * PIXEL_PER_METER)

BACK_DASH_SPEED_KMPH = 10
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
FRAMES_PER_MOVE_JUMP_ACTION = 6

BACK_DASH_TIME_PER_ACTION = 0.3
BACK_DASH_ACTION_PER_TIME = 1.0 / BACK_DASH_TIME_PER_ACTION
FRAMES_PER_BACK_DASH_ACTION = 6

def time_out(e):
    return e[0] == 'TIME_OUT'

def pressing_key(e):
    return e[0] == 'Pressing_Key'

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
        self.character.anim_tick = 0
        self.character.frame = 0
        self.character.jump_frame = 0
        if self.character.right_down(e) or self.character.right_pressed:
            self.character.dir = 1
        elif self.character.left_down(e) or self.character.left_pressed:
            self.character.dir = -1
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
        self.character=character
        self.vy = 0.0
        self.gravity = -1500.0
        self.desired_jump_height = 120
        self.pressed_after_enter = False
        self.pressed_dir = 0
    def enter(self, e):
        self.character.frame = self.character.jump_frame
        self.character.ground_y = self.character.yPos
        g_abs = -self.gravity if self.gravity < 0 else self.gravity
        self.vy = (2 * g_abs * self.desired_jump_height) ** 0.5
        if self.vy < 0:
            self.vy = -self.vy
    def exit(self,e):
        self.character.jump_frame = self.character.frame
        self.character.dir = 0
        pass
    def do(self):
        self.character.frame = (self.character.frame +
                                FRAMES_PER_JUMP_ACTION * JUMP_ACTION_PER_TIME * game_framework.frame_time) \
                               % max(1, self.character.image.jump_frames)
        self.vy += self.gravity * game_framework.frame_time
        self.character.yPos += self.vy * game_framework.frame_time

        if self.character.yPos <= self.character.ground_y:
            self.character.yPos = self.character.ground_y
            if self.character.right_pressed or self.character.left_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Key', None))
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))
        pass
    def draw(self):
        self.character.image.draw_by_frame_num(self.character.image.jump_frame_start + int(self.character.frame),self.character.xPos, self.character.yPos,self.character.face_dir)
        pass

class MoveJump:
    def __init__(self, character):
        self.character=character
        self.vy = 0.0
        self.gravity = -1500.0
        self.desired_jump_height = 120
    def enter(self, e):
        self.character.frame = self.character.jump_frame
        self.character.ground_y = self.character.yPos
        g_abs = -self.gravity if self.gravity < 0 else self.gravity
        self.vy = (2 * g_abs * self.desired_jump_height) ** 0.5
        if self.vy < 0:
            self.vy = -self.vy
        if self.character.right_down(e) or self.character.right_pressed:
            self.character.dir = 1
        elif self.character.left_down(e) or self.character.left_pressed:
            self.character.dir = -1
    def exit(self,e):
        self.character.jump_frame = self.character.frame
        self.character.dir = 0
        pass
    def do(self):
        if self.character.dir == 1:
            self.character.frame = (self.character.frame +
                                    FRAMES_PER_MOVE_JUMP_ACTION * MOVE_JUMP_ACTION_PER_TIME * game_framework.frame_time) \
                                    % max(1, self.character.image.jump_move_frames)
        else:
            self.character.frame = (self.character.frame -
                                    FRAMES_PER_MOVE_JUMP_ACTION * MOVE_JUMP_ACTION_PER_TIME * game_framework.frame_time) \
                                   % max(1, self.character.image.jump_move_frames)
        self.vy += self.gravity * game_framework.frame_time
        self.character.yPos += self.vy * game_framework.frame_time
        self.character.xPos += self.character.dir * WALK_SPEED_PPS * game_framework.frame_time

        if self.character.yPos <= self.character.ground_y:
            self.character.yPos = self.character.ground_y
            if self.character.right_pressed or self.character.left_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Key', None))
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))
        pass
    def draw(self):
            self.character.image.draw_by_frame_num(self.character.image.jump_move_motion_list[int(self.character.frame)],self.character.xPos, self.character.yPos,self.character.face_dir)

class Run:
    def __init__(self, character):
        self.character=character
    def enter(self, e):
        self.character.anim_tick = 0
        self.character.frame = 0
        self.character.jump_frame = 0
        if self.character.right_down(e) or self.character.right_pressed:
            self.character.dir = 1
        elif self.character.left_down(e) or self.character.left_pressed:
            self.character.dir = -1
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
        self.character=character
        self.vy = 0.0
        self.gravity = -1500.0
        self.desired_jump_height = 120
    def enter(self, e):
        self.character.frame = self.character.jump_frame
        self.character.ground_y = self.character.yPos
        g_abs = -self.gravity if self.gravity < 0 else self.gravity
        self.vy = (2 * g_abs * self.desired_jump_height) ** 0.5
        if self.vy < 0:
            self.vy = -self.vy
        if self.character.right_down(e) or self.character.right_pressed:
            self.character.dir = 1
        elif self.character.left_down(e) or self.character.left_pressed:
            self.character.dir = -1
    def exit(self,e):
        self.character.jump_frame = self.character.frame
        self.character.dir = 0
        pass
    def do(self):
        if self.character.dir == 1:
            self.character.frame = (self.character.frame +
                                    FRAMES_PER_MOVE_JUMP_ACTION * MOVE_JUMP_ACTION_PER_TIME * game_framework.frame_time) \
                                    % max(1, self.character.image.jump_move_frames)
        else:
            self.character.frame = (self.character.frame -
                                    FRAMES_PER_MOVE_JUMP_ACTION * MOVE_JUMP_ACTION_PER_TIME * game_framework.frame_time) \
                                   % max(1, self.character.image.jump_move_frames)
        self.vy += self.gravity * game_framework.frame_time
        self.character.yPos += self.vy * game_framework.frame_time
        self.character.xPos += self.character.dir * RUN_SPEED_PPS * game_framework.frame_time

        if self.character.yPos <= self.character.ground_y:
            self.character.yPos = self.character.ground_y
            if self.character.right_pressed or self.character.left_pressed:
                self.character.state_machine.handle_state_event(('Pressing_Key', None))
            else:
                self.character.state_machine.handle_state_event(('TIME_OUT', None))
        pass
    def draw(self):
            self.character.image.draw_by_frame_num(self.character.image.jump_move_motion_list[int(self.character.frame)],self.character.xPos, self.character.yPos,self.character.face_dir)

class BackDash:
    def __init__(self, character):
        self.character = character
        self.vy = 0.0
        self.gravity = -1500.0
        self.desired_jump_height = 120
        self.pressed_after_enter = False
        self.pressed_dir = 0
    def enter(self, e):
        if self.character.right_down(e) or self.character.right_pressed:
            self.character.dir = 1
        elif self.character.left_down(e) or self.character.left_pressed:
            self.character.dir = -1
        pass
    def exit(self,e):
        self.character.dir = 0
        pass
    def do(self):
        self.character.xPos -= self.character.dir * BACK_DASH_SPEED_PPS * game_framework.frame_time
        pass
    def draw(self):
        self.character.image.draw_by_frame_num(self.character.image.back_dash_frame_start,self.character.xPos, self.character.yPos,self.character.face_dir)
        pass

class Character:
    def __init__(self, image_data,keymap=None):
        default = {'left': SDLK_LEFT, 'right': SDLK_RIGHT, 'up': SDLK_UP}
        self.font = load_font('ENCR10B.TTF', 16)
        self.keymap = default if keymap is None else {**default, **keymap}
        self.xPos = 400
        self.yPos = 90
        self.frame = 0
        self.face_dir = -1
        self.dir = 0
        self.image=image_data
        self.jump_frame=0
        self.ground_y =0
        self.anim_tick=0
        self.anim_delay=4
        self.double_tap_interval=0.3

        self._last_down = {}  # key_const -> 마지막 다운 시각
        self._last_up = {}  # key_const -> 마지막 업 시각

        self.left_pressed = False
        self.right_pressed = False

        self.require_up_between_double = False  # True로 하면 기존 동작(중간에 KEYUP 필요)로 강제

        self.IDLE=Idle(self)
        self.WALK=Walk(self)
        self.JUMP=Jump(self)
        self.MOVE_JUMP=MoveJump(self)
        self.RUN = Run(self)
        self.RUN_JUMP = RunJump(self)
        self.BACK_DASH = BackDash(self)

        def mk_key_pred(key_const, sdl_type):
            def pred(e):
                return e[0] == 'INPUT' and e[1].type == sdl_type and e[1].key == key_const
            return pred

        def mk_double_tap_pred(key_const, sdl_type, forward_check=True):
            # key_const로부터 키 방향 결정(오른쪽=1, 왼쪽=-1)
            key_dir = 1 if key_const == self.keymap['right'] else -1

            def pred(e):
                if not (e[0] == 'INPUT' and e[1].type == sdl_type and e[1].key == key_const):
                    return False
                if sdl_type == SDL_KEYDOWN:
                    now = get_time()
                    prev_down = self._last_down.get(key_const, 0)
                    prev_up = self._last_up.get(key_const, 0)

                    # 두 번의 DOWN이 인터벌 내에 있으면 더블로 본다.
                    # 필요하면 중간에 UP이 있었는지도 검사하도록 플래그로 제어.
                    within_interval = (prev_down != 0) and ((now - prev_down) <= self.double_tap_interval)
                    require_up = getattr(self, 'require_up_between_double', False)
                    had_up_between = (prev_up > prev_down)
                    is_double = within_interval and ((not require_up) or had_up_between)

                    # 최신 다운 시간은 항상 갱신
                    self._last_down[key_const] = now

                    if not is_double:
                        return False

                    # 눌린 키 방향과 현재 시선(face_dir) 비교 → 앞/뒤 판정
                    return (key_dir == self.face_dir) if forward_check else (key_dir != self.face_dir)
                return False

            return pred

        self.right_double_fwd = mk_double_tap_pred(self.keymap['right'], SDL_KEYDOWN, forward_check=True)
        self.right_double_back = mk_double_tap_pred(self.keymap['right'], SDL_KEYDOWN, forward_check=False)
        self.left_double_fwd = mk_double_tap_pred(self.keymap['left'], SDL_KEYDOWN, forward_check=True)
        self.left_double_back = mk_double_tap_pred(self.keymap['left'], SDL_KEYDOWN, forward_check=False)

        self.right_down = mk_key_pred(self.keymap['right'], SDL_KEYDOWN)
        self.left_down = mk_key_pred(self.keymap['left'], SDL_KEYDOWN)
        self.right_up = mk_key_pred(self.keymap['right'], SDL_KEYUP)
        self.left_up = mk_key_pred(self.keymap['left'], SDL_KEYUP)
        self.up_down = mk_key_pred(self.keymap['up'], SDL_KEYDOWN)

        self.state_machine = StateMachine(
            self.IDLE,{
                self.IDLE:{self.right_double_fwd:self.RUN,self.left_double_fwd:self.RUN,self.right_double_back:self.BACK_DASH,self.left_double_back:self.BACK_DASH,
                           self.right_down:self.WALK,self.left_down:self.WALK,self.up_down:self.JUMP},
                self.WALK:{self.right_up:self.IDLE,self.left_up:self.IDLE,self.up_down:self.MOVE_JUMP,
                           },
                self.JUMP:{time_out: self.IDLE, pressing_key:self.WALK},
                self.MOVE_JUMP: {time_out:self.IDLE, pressing_key:self.WALK},
                self.RUN:{self.right_up:self.IDLE,self.left_up:self.IDLE,self.up_down:self.RUN_JUMP},
                self.RUN_JUMP:{time_out:self.IDLE,pressing_key:self.RUN},
                self.BACK_DASH:{time_out:self.IDLE,pressing_key:self.WALK}
            }
        )
    def update(self):
        self.state_machine.update()
    def draw(self):
        self.state_machine.draw()
        self.font.draw(self.xPos - 60, self.yPos + 70, f'(Time: {get_time():.2f})', (255, 255, 0))
    def handle_event(self,event):
        if event.type == SDL_KEYDOWN:
            if event.key == self.keymap['left']:
                self.left_pressed = True
            elif event.key == self.keymap['right']:
                self.right_pressed = True
        elif event.type == SDL_KEYUP:
            if event.key == self.keymap['left']:
                self.left_pressed = False
                self._last_up[self.keymap['left']] = get_time()
            elif event.key == self.keymap['right']:
                self.right_pressed = False
                self._last_up[self.keymap['right']] = get_time()
        self.state_machine.handle_state_event(('INPUT', event))