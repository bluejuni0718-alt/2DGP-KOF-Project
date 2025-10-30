from pico2d import *
from frame import *
from state_machine import *
from character_frame import *

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
        self.character.anim_tick += 1
        if self.character.anim_tick >= self.character.anim_delay:
            self.character.anim_tick = 0
            self.character.frame=(self.character.frame + 1) % max(1, self.character.image.walk_frames)
            self.character.xPos+=self.character.dir*5
        pass
    def draw(self):
        self.character.image.draw_walk_by_frame_num(self.character.frame, self.character.xPos, self.character.yPos,self.character.face_dir,self.character.dir)
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
            print(self.character.frame)
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
        self.character.image.draw_jump_by_frame_num(self.character.frame, self.character.xPos, self.character.yPos,self.character.face_dir)
        pass

class MoveJump:
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
        self.character.dir = 0
        pass
    def do(self):
        pass
    def draw(self):
        pass

class Character:
    def __init__(self, image_data,keymap=None):
        default = {'left': SDLK_LEFT, 'right': SDLK_RIGHT, 'up': SDLK_UP}
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

        self.left_pressed = False
        self.right_pressed = False

        self.IDLE=Idle(self)
        self.WALK=Walk(self)
        self.JUMP=Jump(self)

        def mk_key_pred(key_const, sdl_type):
            def pred(e):
                return e[0] == 'INPUT' and e[1].type == sdl_type and e[1].key == key_const
            return pred

        self.right_down = mk_key_pred(self.keymap['right'], SDL_KEYDOWN)
        self.left_down = mk_key_pred(self.keymap['left'], SDL_KEYDOWN)
        self.right_up = mk_key_pred(self.keymap['right'], SDL_KEYUP)
        self.left_up = mk_key_pred(self.keymap['left'], SDL_KEYUP)
        self.up_down = mk_key_pred(self.keymap['up'], SDL_KEYDOWN)

        self.state_machine = StateMachine(
            self.IDLE,{
                self.IDLE:{self.right_down:self.WALK,self.left_down:self.WALK,self.up_down:self.JUMP},
                self.WALK:{self.right_up:self.IDLE,self.left_up:self.IDLE,self.up_down:self.JUMP},
                self.JUMP:{time_out: self.IDLE, pressing_key:self.WALK}
            }
        )
    def update(self):
        self.state_machine.update()
    def draw(self):
        self.state_machine.draw()
    def handle_event(self,event):
        if event.type == SDL_KEYDOWN:
            if event.key == self.keymap['left']:
                self.left_pressed = True
            elif event.key == self.keymap['right']:
                self.right_pressed = True
        elif event.type == SDL_KEYUP:
            if event.key == self.keymap['left']:
                self.left_pressed = False
            elif event.key == self.keymap['right']:
                self.right_pressed = False
        self.state_machine.handle_state_event(('INPUT', event))