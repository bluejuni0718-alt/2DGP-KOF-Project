from pico2d import draw_rectangle

class HitBox:
    def __init__(self, owner, hb_kind:str, rect:tuple[float, float, float, float]):
        self.owner = owner
        self.hb_kind = hb_kind
        self.rect = rect
    def update(self, new_rect:tuple[float, float, float, float]):
        self.rect = new_rect


class HitBoxManager:
    def __init__(self):
        self.hitboxes = []

    def register_hitbox(self, hitbox: HitBox):
        self.hitboxes.append(hitbox)

    def debug_draw(self):
        for hb in self.hitboxes:
            draw_rectangle(hb.rect[0], hb.rect[1], hb.rect[0] + hb.rect[2], hb.rect[1] + hb.rect[3])
    def collision_check(self, hb1: HitBox, hb2: HitBox) -> bool:
        r1 = hb1.rect
        r2 = hb2.rect
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2