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


class InteractionManager:
    """
    사용법:
      im = InteractionManager(renderer=None)
      im.on('enter', lambda a,b: print('enter', a.hb_id, b.hb_id))
      매 프레임:
        im.begin_frame()
        for each object: im.register_hitbox(owner, hb_id, rect=(l,b,w,h), tag=...)
        im.process()
        im.debug_draw()
    """
    def __init__(self, renderer: Optional[Callable] = None):
        self.renderer = renderer if callable(renderer) else None
        self._hitboxes: List[Hitbox] = []
        self._prev_pairs: set = set()  # set of normalized pair keys
        self._last_hitbox_map: Dict[Tuple[int, str], Hitbox] = {}
        self._callbacks: Dict[str, List[Callable[[Hitbox, Hitbox], None]]] = {'enter': [], 'stay': [], 'exit': []}

    def begin_frame(self) -> None:
        self._hitboxes = []

    def register_hitbox(self, owner: Any, hb_id: str, rect: Optional[Tuple[float, float, float, float]] = None,
                        tag: Optional[str] = None, use_frame_size: bool = False) -> None:
        """
        rect가 None이고 use_frame_size=True면 owner의 frame_list/frame 정보를 사용해서 (w,h) 계산.
        register된 rect는 월드 좌표의 (left, bottom, width, height)여야 함.
        """
        if rect is None and use_frame_size:
            size = self._get_frame_size_from_owner(owner)
            if not size:
                return
            w, h = size
            img = getattr(owner, 'image', owner)
            delx = float(getattr(img, 'delXPos', 0.0))
            dely = float(getattr(img, 'delYPos', 0.0))
            cx = float(getattr(owner, 'xPos', 0.0)) + delx
            cy = float(getattr(owner, 'yPos', 0.0)) + dely
            l = cx - (w / 2.0)
            b = cy - (h / 2.0)
            rect = (l, b, w, h)
        if rect is None:
            return
        hb = Hitbox(owner, hb_id, rect, tag=tag)
        self._hitboxes.append(hb)

    def on(self, event: str, callback: Callable[[Hitbox, Hitbox], None]) -> None:
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def process(self) -> None:
        curr_pairs = set()
        curr_map: Dict[Tuple[int, str], Hitbox] = {}
        n = len(self._hitboxes)
        for hb in self._hitboxes:
            key = (id(hb.owner), hb.hb_id)
            curr_map[key] = hb

        for i in range(n):
            a = self._hitboxes[i]
            for j in range(i + 1, n):
                b = self._hitboxes[j]
                if a.owner is b.owner:
                    continue
                if a.intersects(b):
                    key = self._pair_key(a, b)
                    curr_pairs.add(key)
                    if key not in self._prev_pairs:
                        self._emit('enter', a, b)
                    else:
                        self._emit('stay', a, b)

        # exit: 이전 프레임에 존재했지만 이번엔 없는 쌍
        for key in list(self._prev_pairs):
            if key not in curr_pairs:
                (a_k, b_k) = key
                a = self._last_hitbox_map.get(a_k)
                b = self._last_hitbox_map.get(b_k)
                if a and b:
                    self._emit('exit', a, b)

        self._prev_pairs = curr_pairs
        self._last_hitbox_map = curr_map

    def debug_draw(self) -> None:
        for hb in self._hitboxes:
            l, b, r, t = hb.as_bbox()
            if self.renderer:
                try:
                    # 기대되는 renderer 시그니처: renderer(left, bottom, right, top, color=color, tag=...)
                    try:
                        self.renderer(l, b, r, t, color=(0, 255, 0), tag=hb.hb_id)
                    except TypeError:
                        # keyword 인자 미지원 시 positional fallback
                        self.renderer(l, b, r, t)
                except Exception:
                    logger.exception("renderer failed for hitbox %s:%s", id(hb.owner), hb.hb_id)
            else:
                # 간단한 콘솔 출력: pico2d 의존 제거
                print(f"HB {id(hb.owner)}:{hb.hb_id} -> {l},{b},{r},{t}")

    # --- 내부 유틸리티 ---
    def _emit(self, event: str, a: Hitbox, b: Hitbox) -> None:
        for cb in self._callbacks.get(event, []):
            try:
                cb(a, b)
            except Exception:
                logger.exception("callback failed for event %s (%s)", event, cb)

    def _pair_key(self, a: Hitbox, b: Hitbox) -> Tuple[Tuple[int, str], Tuple[int, str]]:
        ak = (id(a.owner), a.hb_id)
        bk = (id(b.owner), b.hb_id)
        return (ak, bk) if ak <= bk else (bk, ak)

    def _get_frame_size_from_owner(self, owner: Any) -> Optional[Tuple[float, float]]:
        """
        owner.frame_list[frame_index]가 tuple/list (fx,fy,fw,fh) 또는 객체형 프레임 정보를 지원.
        또한 owner.image.frame_list를 참조할 수 있음.
        반환: (w, h) 또는 None
        """
        try:
            fl = getattr(owner, "frame_list", None)
            idx = getattr(owner, "frame_index", None)
            if fl is not None and idx is not None and 0 <= idx < len(fl):
                f = fl[idx]
                if isinstance(f, (tuple, list)) and len(f) >= 4:
                    return (float(f[2]), float(f[3]))
                return (float(getattr(f, "w", getattr(f, "width", 0))),
                        float(getattr(f, "h", getattr(f, "height", 0))))
        except Exception:
            logger.exception("error reading owner.frame_list")

        try:
            img = getattr(owner, "image", None)
            if img is not None:
                fl = getattr(img, "frame_list", None)
                idx = getattr(owner, "frame_index", None) or getattr(img, "frame_index", None)
                if fl is not None and idx is not None and 0 <= idx < len(fl):
                    f = fl[idx]
                    if isinstance(f, (tuple, list)) and len(f) >= 4:
                        return (float(f[2]), float(f[3]))
                    return (float(getattr(f, "w", getattr(f, "width", 0))),
                            float(getattr(f, "h", getattr(f, "height", 0))))
        except Exception:
            logger.exception("error reading image.frame_list")

        return None