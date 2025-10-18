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
        pass

class Character:
    def __init__(self, image_data):
        self.xPos = 400
        self.yPos = 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 1
        self.image=image_data
        pass

