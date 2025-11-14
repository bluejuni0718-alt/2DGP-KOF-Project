from pico2d import *
from typing import Tuple, Set
import pico2d

class Hitbox:
    def __init__(self, left: float, top: float, right: float, bottom: float, owner=None):
        # pico2d draw_rectangle expects (left, bottom, right, top)
        self.left = float(left)
        self.top = float(top)
        self.right = float(right)
        self.bottom = float(bottom)
        self.owner = owner

    def overlaps(self, other: "Hitbox") -> bool:
        return not (self.right < other.left or self.left > other.right or self.bottom > other.top or self.top < other.bottom)

    def draw_debug(self, color=(255, 0, 0)):
        # color unused by pico2d.draw_rectangle, but kept for API parity
        try:
            pico2d.draw_rectangle(self.left, self.bottom, self.right, self.top)
        except Exception:
            pass

    def __repr__(self):
        return f"Hitbox({self.left}, {self.top}, {self.right}, {self.bottom}, owner={self.owner})"
