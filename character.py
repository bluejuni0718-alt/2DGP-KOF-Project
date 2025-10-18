from pico2d import *
from frame import *

class Character:
    def __init__(self, image_data):
        self.xPos = 400
        self.yPos = 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 1
        self.image=image_data
        pass