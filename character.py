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

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0/TIME_PER_ACTION
FRAMES_PER_ACTION = 8

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
        self.character.anim_tick+=1
        if self.character.anim_tick>=self.character.anim_delay:
            self.character.anim_tick =0
            self.character.frame = (self.character.frame + 1) % max(1, self.character.image.idle_frames)
        pass
    def draw(self):
        self.character.image.draw_idle_by_frame_num(self.character.frame, self.character.xPos, self.character.yPos,self.character.face_dir)
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
        if self.character.anim_tick>=self.character.anim_delay:
            self.character.frame = (self.character.frame + 1) % self.character.image.walk_frames
            self.character.anim_tick =0
        self.character.anim_tick +=1
        self.character.xPos +=self.character.dir * WALK_SPEED_PPS * game_framework.frame_time
        pass
    def draw(self):
        self.character.image.draw_by_act_kind(self.character.image.walk_frame_start,self.character.image.walk_frames ,self.character.frame,self.character.xPos, self.character.yPos,self.character.face_dir)
        pass

class Jump:
    def __init__(self, character):
        self.character=character
    def enter(self, e):
        self.character.anim_delay = 8
        self.character.anim_tick = 0
        self.character.frame = self.character.jump_frame
        pass
    def exit(self,e):
        self.character.anim_delay = 4
        self.character.jump_frame = self.character.frame
        self.character.dir =0
        pass
    def do(self):
        self.character.anim_tick += 1
        if self.character.anim_tick >= self.character.anim_delay:
            self.character.anim_tick = 0
            self.character.frame = (self.character.frame + 1) % max(1, self.character.image.jump_frames)
        if self.character.anim_tick >= self.character.anim_delay/3:
            if self.character.frame<=1:
                self.character.yPos += 12.5
            elif self.character.frame<=3:
                self.character.yPos -= 12.5
        if self.character.frame == 4 and (self.character.left_pressed==False and self.character.right_pressed==False):
            self.character.state_machine.handle_state_event(('TIME_OUT', None))
        elif self.character.frame == 4 and (self.character.right_pressed==True or self.character.left_pressed==True):
            self.character.state_machine.handle_state_event(('Pressing_Key', None))
        pass
    def draw(self):
        self.character.image.draw_by_act_kind(self.character.image.jump_frame_start,self.character.image.jump_frames ,self.character.frame,self.character.xPos, self.character.yPos,self.character.face_dir)
        pass

class MoveJump:
    def __init__(self, character):
        self.character=character
        self.SpecialFrame= 0
    def enter(self, e):
        self.character.anim_tick = 0
        self.character.frame = self.character.jump_frame
        if self.character.right_pressed:
            self.character.dir = 1
        elif self.character.left_pressed:
            self.character.dir = -1
        pass
    def exit(self,e):
        self.character.jump_frame = self.character.frame
        self.character.dir = 0
        pass
    def do(self):
        self.character.anim_tick += 1
        if self.character.anim_tick >= self.character.anim_delay:
            self.character.anim_tick = 0
            self.character.frame = (self.character.frame + 1) % max(1, self.character.image.jump_move_frames + 1)
        if self.character.anim_tick >= self.character.anim_delay/2:
            self.character.xPos += self.character.dir * 5
            if self.character.frame <= 3:
                self.character.yPos += 17.5
            elif self.character.frame <= 7:
                self.character.yPos -= 17.5
            else:
                if self.character.left_pressed == False and self.character.right_pressed == False:
                    self.character.state_machine.handle_state_event(('TIME_OUT', None))
                elif self.character.right_pressed == True or self.character.left_pressed == True:
                    self.character.state_machine.handle_state_event(('Pressing_Key', None))
        pass
    def draw(self):
        frame_count = max(1, self.character.image.jump_move_frames)
        relative_frame = self.character.frame % frame_count

        if 1 < relative_frame < 6:
            self.SpecialFrame = 54
        else:
            self.SpecialFrame = 0

        draw_frame = relative_frame
        if self.character.dir == -1:
            draw_frame = frame_count - 1 - relative_frame

        start = self.character.image.jump_move_frame_start + self.SpecialFrame

        self.character.image.draw_by_act_kind(start, frame_count, draw_frame,
                                              self.character.xPos, self.character.yPos,
                                              self.character.face_dir)

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
        if self.character.anim_tick >= self.character.anim_delay:
            self.character.frame = (self.character.frame + 1) % self.character.image.walk_frames
            self.character.anim_tick = 0
        self.character.anim_tick += 1
        self.character.xPos += self.character.dir * RUN_SPEED_PPS * game_framework.frame_time
        pass
    def draw(self):
        self.character.image.draw_by_act_kind(self.character.image.run_frame_start,self.character.image.run_frames ,self.character.frame,self.character.xPos, self.character.yPos,self.character.face_dir)
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
        self.anim_tick=0
        self.anim_delay=4
        self.double_tap_interval=0.3

        self._last_down = {}  # key_const -> 마지막 다운 시각
        self._last_up = {}  # key_const -> 마지막 업 시각

        self.left_pressed = False
        self.right_pressed = False

        self.IDLE=Idle(self)
        self.WALK=Walk(self)
        self.JUMP=Jump(self)
        self.MOVE_JUMP=MoveJump(self)
        self.RUN = Run(self)

        def mk_key_pred(key_const, sdl_type):
            def pred(e):
                return e[0] == 'INPUT' and e[1].type == sdl_type and e[1].key == key_const
            return pred

        def mk_double_tap_pred(key_const, sdl_type, required_face_dir=None, must_match=True):
            def pred(e):
                if not (e[0] == 'INPUT' and e[1].type == sdl_type and e[1].key == key_const):
                    return False
                if sdl_type == SDL_KEYDOWN:
                    now = get_time()
                    prev_down = self._last_down.get(key_const, 0)
                    prev_up = self._last_up.get(key_const, 0)
                    is_double = (prev_down != 0) and ((now - prev_down) <= self.double_tap_interval) and (
                                prev_up > prev_down)
                    self._last_down[key_const] = now
                    if not is_double:
                        return False
                    if required_face_dir is None:
                        return True
                    return (self.face_dir == required_face_dir) if must_match else (self.face_dir != required_face_dir)
                return False
            return pred

        self.right_double_fwd = mk_double_tap_pred(self.keymap['right'], SDL_KEYDOWN, required_face_dir=1, must_match=False)
        self.right_double_back = mk_double_tap_pred(self.keymap['right'], SDL_KEYDOWN, required_face_dir=1,must_match=True)
        # 왼쪽 키: 앞이면 face_dir == -1, 뒤면 face_dir != -1
        self.left_double_fwd = mk_double_tap_pred(self.keymap['left'], SDL_KEYDOWN, required_face_dir=-1, must_match=False)
        self.left_double_back = mk_double_tap_pred(self.keymap['left'], SDL_KEYDOWN, required_face_dir=-1, must_match=True)

        self.right_down = mk_key_pred(self.keymap['right'], SDL_KEYDOWN)
        self.left_down = mk_key_pred(self.keymap['left'], SDL_KEYDOWN)
        self.right_up = mk_key_pred(self.keymap['right'], SDL_KEYUP)
        self.left_up = mk_key_pred(self.keymap['left'], SDL_KEYUP)
        self.up_down = mk_key_pred(self.keymap['up'], SDL_KEYDOWN)

        self.state_machine = StateMachine(
            self.IDLE,{
                self.IDLE:{self.right_double_fwd:self.RUN,self.left_double_fwd:self.RUN,self.right_down:self.WALK,self.left_down:self.WALK,self.up_down:self.JUMP},
                self.WALK:{self.right_up:self.IDLE,self.left_up:self.IDLE,self.up_down:self.MOVE_JUMP},
                self.JUMP:{time_out: self.IDLE, pressing_key:self.WALK},
                self.MOVE_JUMP: {time_out:self.IDLE, pressing_key:self.WALK},
                self.RUN:{self.right_up:self.IDLE,self.left_up:self.IDLE}
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