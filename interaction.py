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

    def detect_is_opponent_attacking(self):
        main_boxes = [hb for hb in self.hitboxes if hb.hb_kind == 'body']
        box_1 = main_boxes[0]
        box_2 = main_boxes[1]
        ch_1 = box_1.owner
        ch_2 = box_2.owner
        if ch_1.is_attacking :
            ch_2.is_opponent_attacking = True
        else:
            ch_2.is_opponent_attacking = False
        if ch_2.is_attacking :
            ch_1.is_opponent_attacking = True
        else:
            ch_1.is_opponent_attacking = False

    def detect_body_overlaps(self):
        boxes = [hb for hb in self.hitboxes if hb.hb_kind == 'body']
        box_1 = boxes[0]
        box_2 = boxes[1]
        ch_1 = box_1.owner
        ch_2 = box_2.owner

        if self.collision_check(box_1, box_2):
            if ch_1.vy ==0 or ch_1.vy ==0:
                if ch_1.xPos < ch_2.xPos:
                    overlap_x = min(box_1.rect[0] + box_1.rect[2], box_2.rect[0] + box_2.rect[2]) - max(box_1.rect[0], box_2.rect[0])
                    ch_1.xPos -= overlap_x//2
                    ch_2.xPos += overlap_x//2
                else:
                    overlap_x = min(box_1.rect[0] + box_1.rect[2], box_2.rect[0] + box_2.rect[2]) - max(box_1.rect[0], box_2.rect[0])
                    ch_1.xPos += overlap_x//2
                    ch_2.xPos -= overlap_x//2

    def detect_attack_hits(self):
        body_boxes = [hb for hb in self.hitboxes if hb.hb_kind == 'body']
        body_box_1 = body_boxes[0]
        body_box_2 = body_boxes[1]
        attack_boxes = [hb for hb in self.hitboxes if hb.hb_kind == 'attack']
        if attack_boxes[0].owner == body_box_1.owner:
            attack_box_1 = attack_boxes[0]
            attack_box_2 = attack_boxes[1]
        else:
            attack_box_1 = attack_boxes[1]
            attack_box_2 = attack_boxes[0]
        # TODO: 데미지 처리 및 콤보 가능 구간 설정 필요
        if self.collision_check(attack_box_1, body_box_2) and body_box_2.owner.is_guarding == False:
            body_box_2.owner.is_hitted = True

        if self.collision_check(attack_box_2, body_box_1) and body_box_1.owner.is_guarding == False:
            body_box_1.owner.is_hitted = True



    def update_face_dir(self, ch1, ch2):
        if ch1.xPos < ch2.xPos:
            if ch1.vy ==0:
                ch1.face_dir = 1
            if ch2.vy ==0:
                ch2.face_dir = -1
        else:
            if ch1.vy ==0:
                ch1.face_dir = -1
            if ch2.vy ==0:
                ch2.face_dir = 1
