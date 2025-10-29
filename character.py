from pico2d import *
from frame import *
from state_machine import *
from character_frame import *

def time_out(e):
    return e[0] == 'TIME_OUT'

class Idle:
    def __init__(self, character):
        self.character =character
        pass
    def enter(self, e):
        self.character.anim_tick=0
        self.character.frame =0
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
        if self.character.right_down(e):
            self.character.dir = 1
        elif self.character.left_down(e):
            self.character.dir = -1
        pass
    def exit(self,e):
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
        self.character.anim_delay = 7
        self.character.anim_tick = 0
        self.character.frame = 0
        pass
    def exit(self,e):
        self.character.anim_delay = 4
        pass
    def do(self):
        self.character.anim_tick += 1
        if self.character.anim_tick >= self.character.anim_delay:
            self.character.anim_tick = 0
            self.character.frame = (self.character.frame + 1) % max(1, self.character.image.walk_frames)
            if self.character.frame<=2:
                self.character.yPos += 50
            elif self.character.frame<=4:
                self.character.yPos -= 50
        if self.character.frame == 5:
            self.character.state_machine.handle_state_event(('TIME_OUT', None))
        pass
    def draw(self):
        self.character.image.draw_jump_by_frame_num(self.character.frame, self.character.xPos, self.character.yPos,self.character.face_dir)
        pass

class Character:
    def __init__(self, image_data,keymap=None):
        default = {'left': SDLK_LEFT, 'right': SDLK_RIGHT, 'up': SDLK_UP}
        self.keymap = default if keymap is None else {**default, **keymap}
        self.xPos = 400
        self.yPos = 90
        self.frame = 0
        self.face_dir = -1
        self.dir = 1
        self.image=image_data

        self.anim_tick=0
        self.anim_delay=4

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
                self.WALK:{self.right_up:self.IDLE,self.left_up:self.IDLE, self.up_down:self.JUMP},
                self.JUMP:{time_out:self.IDLE,self.right_down:self.JUMP, self.left_down:self.JUMP, self.right_up:self.JUMP,self.left_up:self.JUMP},
            }
        )
    def update(self):
        self.state_machine.update()
    def draw(self):
        self.state_machine.draw()
    def handle_event(self,event):
        self.state_machine.handle_state_event(('INPUT', event))