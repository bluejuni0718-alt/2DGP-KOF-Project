from pico2d import draw_rectangle

class HitBox:
    def __init__(self, owner, hb_kind:str, rect:tuple[float, float, float, float]):
        self.owner = owner
        self.hb_kind = hb_kind
        self.rect = rect

class HitBoxManager:
    def __init__(self):
        self.hitboxes = []

    def register_hitbox(self, hitbox: HitBox):
        self.hitboxes.append(hitbox)

    def debug_draw(self):
        for hb in self.hitboxes:
            draw_rectangle(hb[0], hb[1], hb[0] + hb[2], hb[1] + hb[3])