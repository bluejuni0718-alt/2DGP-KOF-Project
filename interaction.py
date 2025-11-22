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