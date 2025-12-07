from pico2d import draw_rectangle


class HitBox:
    def __init__(self, owner, hb_kind:str, rect:tuple[float, float, float, float]):
        self.owner = owner
        self.hb_kind = hb_kind
        self.rect = rect
    def update(self, new_rect:tuple[float, float, float, float]):
        self.rect = new_rect
    def reset_rect(self):
        self.rect = (0,0,0,0)

class HitBoxManager:
    def __init__(self):
        self.hitboxes = []

    def register_hitbox(self, hitbox: HitBox):
        self.hitboxes.append(hitbox)

    def debug_draw(self):
        for hb in self.hitboxes:
            draw_rectangle(hb.rect[0], hb.rect[1], hb.rect[0] + hb.rect[2], hb.rect[1] + hb.rect[3])

    def collision_check(self, hb1: HitBox, hb2: HitBox) -> bool:
        x1, y1, w1, h1 = hb1.rect
        x2, y2, w2, h2 = hb2.rect

        # 너비/높이가 음수일 수인 경우도 고려
        left1 = min(x1, x1 + w1)
        right1 = max(x1, x1 + w1)
        bottom1 = min(y1, y1 + h1)
        top1 = max(y1, y1 + h1)

        left2 = min(x2, x2 + w2)
        right2 = max(x2, x2 + w2)
        bottom2 = min(y2, y2 + h2)
        top2 = max(y2, y2 + h2)

        # 두 사각형이 서로 겹치지 않는 조건을 먼저 검사
        no_overlap = (right1 < left2) or (left1 > right2) or (top1 < bottom2) or (bottom1 > top2)

        # no_overlap 가 False 이면 충돌(테두리 맞닿음 포함)
        return not no_overlap

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

        if self.collision_check(box_1, box_2) and ch_1.is_hitted == False and ch_2.is_hitted == False and ch_1.is_attacking == False and ch_2.is_attacking == False:
            if ch_1.vy ==0 or ch_2.vy ==0:
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
        body_box_1, body_box_2 = body_boxes[0], body_boxes[1]

        def handle(ch_1, ch_2):
            target = ch_2
            attacker = ch_1
            if not self.collision_check(ch_1.attack_hitbox,ch_2.body_hitbox):
                return

            if target.is_guarding == True:
                return

            if target.get_damage == False:
                return

            target.is_hitted = True
            attacker.is_succeeded_attack = True
            target.hp -= attacker.atk
            target.get_damage = False
            target.xPos += (40 * attacker.face_dir)  # 넉백 효과
            target.state_machine.handle_state_event(('HITTED', None))

        handle(body_box_1.owner, body_box_2.owner)
        handle(body_box_2.owner, body_box_1.owner)


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