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
class InteractionManager:
    def __init__(self):
        # (attacker id, frame_id) 쌍으로 같은 애니 내 중복 히트 방지
        self._already_hit: Set[tuple] = set()

    def clear_frame_hits(self):
        """매 프레임 시작 시 호출하여 중복 히트 기록 초기화"""
        self._already_hit.clear()

    def _absolute_hitbox_from_relative(self, attacker, rel: Tuple[float, float, float, float]):
        """rel: (ox, oy, w, h) - 공격자 기준 상대 박스를 월드 좌표 Hitbox로 변환"""
        ox, oy, w, h = rel
        face = getattr(attacker, "face_dir", 1)
        ox_world = attacker.xPos + (ox * face)
        top = attacker.yPos + oy + h / 2
        bottom = attacker.yPos + oy - h / 2
        left = ox_world - w / 2
        right = ox_world + w / 2
        return Hitbox(left=left, top=top, right=right, bottom=bottom, owner=attacker)
