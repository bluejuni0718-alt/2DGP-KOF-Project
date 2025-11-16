# python
# 파일: `interaction.py`
from typing import Callable, Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class Hitbox:
    """
    rect: (left, bottom, width, height)
    owner: 어떤 게임 오브젝트(캐릭터) 인스턴스
    hb_id: 히트박스 식별자(문자열 등)
    tag: 선택적 태그
    """
    def __init__(self, owner: Any, hb_id: str, rect: Tuple[float, float, float, float], tag: Optional[str] = None):
        self.owner = owner
        self.hb_id = hb_id
        self.rect = (float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3]))
        self.tag = tag

    def as_bbox(self) -> Tuple[float, float, float, float]:
        l, b, w, h = self.rect
        return (l, b, l + w, b + h)  # left, bottom, right, top

    def intersects(self, other: "Hitbox") -> bool:
        l1, b1, r1, t1 = self.as_bbox()
        l2, b2, r2, t2 = other.as_bbox()
        return not (r1 <= l2 or r2 <= l1 or t1 <= b2 or t2 <= b1)

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

    def _hurtbox_of(self, target):
        """target.get_hurtbox() 우선 사용, 없으면 image 기반 폴백 박스 생성"""
        if hasattr(target, "get_hurtbox"):
            return target.get_hurtbox()
        frame_idx = int(getattr(target, "frame", 0))
        image = getattr(target, "image", None)
        hb_list = getattr(image, "hurtboxes", None) if image is not None else None
        if hb_list and frame_idx < len(hb_list):
            ox, oy, w, h = hb_list[frame_idx]
        else:
            w = getattr(image, "frame_w", 40) if image is not None else 40
            h = getattr(image, "frame_h", 80) if image is not None else 80
            ox, oy = 0, 0
        left = target.xPos + ox - w / 2
        right = target.xPos + ox + w / 2
        top = target.yPos + oy + h / 2
        bottom = target.yPos + oy - h / 2
        return Hitbox(left=left, top=top, right=right, bottom=bottom, owner=target)

    def check_and_resolve(self, attacker, target):
        """
        매 프레임 루프에서 attacker/target 쌍마다 호출.
        attacker.get_current_attack_info() -> None 또는 dict:
          {
            "frame_id": any_unique_identifier,
            "relative_box": (ox, oy, w, h),
            "damage": int,
            "knockback": (dx, dy),
            "hitstun": float_seconds
          }
        """
        info = attacker.get_current_attack_info() if hasattr(attacker, "get_current_attack_info") else None
        if not info:
            return

        frame_id = info.get("frame_id")
        key = (id(attacker), frame_id)
        if key in self._already_hit:
            return

        rel = info.get("relative_box")
        if not rel:
            return

        atk_box = self._absolute_hitbox_from_relative(attacker, rel)
        tgt_box = self._hurtbox_of(target)

        if atk_box.overlaps(tgt_box):
            knock = info.get("knockback", (0.0, 0.0))
            damage = info.get("damage", 0)
            hitstun = info.get("hitstun", 0.0)

            if hasattr(attacker, "on_hit_success"):
                try:
                    attacker.on_hit_success(target, info)
                except Exception:
                    pass

            if hasattr(target, "apply_hit"):
                abs_knock_x = knock[0] * getattr(attacker, "face_dir", 1)
                abs_knock_y = knock[1]
                target.apply_hit({
                    "from": attacker,
                    "damage": damage,
                    "knockback": (abs_knock_x, abs_knock_y),
                    "hitstun": hitstun,
                    "hit_time": pico2d.get_time()
                })

            self._already_hit.add(key)