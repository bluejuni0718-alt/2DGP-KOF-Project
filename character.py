from pico2d import *
from frame import *
from state_machine import *
from character_frame import *

class Idle:
    def __init__(self, character):
        self.character =character
        pass
    def enter(self, e):
        pass
    def do(self):
        self.character.frame = (self.character.frame + 1) % self.character.image.idle_frames
        pass
    def draw(self):
        self.character.image.draw_idle_by_frame_num(self.character.frame, self.character.xPos, self.character.yPos,self.character.face_dir)
        pass

class Character:
    def __init__(self, image_data,keymap=None):
        default = {'left': SDLK_LEFT, 'right': SDLK_RIGHT, 'space': SDLK_SPACE}
        self.keymap = default if keymap is None else {**default, **keymap}
        self.xPos = 400
        self.yPos = 90
        self.frame = 0
        self.face_dir = -1
        self.dir = 1
        self.image=image_data

        self.IDLE=Idle(self)

        def mk_key_pred(key_const, sdl_type):
            def pred(e):
                return e[0] == 'INPUT' and e[1].type == sdl_type and e[1].key == key_const
            return pred

        right_down = mk_key_pred(self.keymap['right'], SDL_KEYDOWN)
        left_down=mk_key_pred(self.keymap['left'], SDL_KEYDOWN)

        self.state_machine = StateMachine(
            self.IDLE,{
                self.IDLE:{}
            }
        )
    def update(self):
        self.state_machine.update()
    def draw(self):
        self.state_machine.draw()
    def handle_event(self,event):
        self.state_machine.handle_state_event(('INPUT', event))