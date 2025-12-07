from matplotlib.pyplot import margins
from pico2d import load_image, get_canvas_width, get_canvas_height, clamp
import common
from game_framework import frame_time

class PalaceMap:
    def __init__(self, margin = 50):
        self.image = load_image('GameMode_image/Game_Play_Map.png')
        self.cw = get_canvas_width()
        self.ch = get_canvas_height()
        self.w = self.image.w
        self.h = self.image.h
        self.margin = margin
        self.window_left = 0
        self.window_bottom = 0
