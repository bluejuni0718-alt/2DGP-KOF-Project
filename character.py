from pico2d import *
from frame import *

class Character:
    def __init__(self, alpha_image_path, frame_image_path):
        self.xPos = 400
        self.yPos = 90
        self.frame = 0
        self.face_dir = 1
        self.image = load_image(alpha_image_path)
        self.frame_list = get_frame_list(frame_image_path)
        pass