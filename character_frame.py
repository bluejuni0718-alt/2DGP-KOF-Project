from pico2d import *
from frame import *

CHARACTER_HEIGHT_SCALE = 2.0
CHARACTER_WIDTH_SCALE = 2.0

class KimFrameInfo:
    def __init__(self,frame_list_path='CharacterSpriteSheet_Modified/Kim_frame_box.png', print_image_path='CharacterSpriteSheet_Modified/Kim_frames_alpha1.png'):
        self.frame_list = get_frame_list(frame_list_path)
        self.print_image = load_image(print_image_path)
        self.idle_frame_start= 307
        self.idle_frames = 6
        self.walk_frame_start = 85
        self.walk_frames = 6
        self.jump_frame_start = 97
        self.jump_frames = 5
        self.jump_move_motion_list = [97, 98, 153, 154, 155, 156, 100]
        self.jump_move_frame_start = 0
        self.jump_move_frames = 7
        self.run_frame_start= 73
        self.run_frames = 6
        self.back_dash_frame_start = 378
        self.sit_down_frame_start = 0
        self.sit_down_frames = 3
        self.dead_frame = 27
        #방향에 따른 공격값 -> face방향에 따라 반대면 배열의 뒤에서 부터 접근하기?
        self.normal_attacks = {
            'rp': {'frames': [244, 245, 244], 'offsets': [(0, 0), (8, 0), (0, 0)]},
            'lp': {'frames':[259,258,259],'offsets':[(0, 0), (8, 0), (0, 0)]},
            'lk': {'frames':[286,287,288,289,290],'offsets':[(0,0),(0,0),(-10,0),(0,0),(0,0)]},
            'rk': {'frames': [254,255,256,255,254], 'offsets': [(0, 0), (8, 0), (0, 0), (8, 0), (0, 0)]},
        }
        self.jump_attacks ={
            'rp': {'frames': [250, 251, 251,251,251], 'offsets': [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]},
            'lp': {'frames':[260,261,260],'offsets':[(0, 0), (0, 0), (0, 0)]},
            'lk': {'frames':[352,353,354,355],'offsets':[(0,0),(8,0),(0,0),(0,0)]},
            'rk': {'frames': [275,276,277], 'offsets': [(0, 0),(0, 0),  (0, 0)]},
        }
        self.move_jump_attacks={
            'rp': {'frames': [250, 251, 251,251,251], 'offsets': [(0, 0), (8, 0), (0, 0), (8, 0), (0, 0)]},
            'lp': {'frames':[260,261,260],'offsets':[(0, 0), (8, 0), (0, 0)]},
            'lk': {'frames':[352,353,379,379,379,379],'offsets':[(0,-20),(0,-20),(0,-20),(0,-20),(0,-20),(0,-20)]},
            'rk': {'frames':[272,273,274,214,215,216], 'offsets':[(0,0),(0,0),(0,0),(0,0)]},
        }
        self.sit_attacks = {
            'rp': {'frames':[252,253,252],'offsets':[(0,-20),(14,-24),(4,-20)]},
            'lp': {'frames':[262,263,262],'offsets':[(20,-10),(30,-10),(20,-10)]},
            'lk': {'frames': [294,295,296,297,298,299], 'offsets': [(0,-10),(0,-10),(0,-10),(0,-10),(0,-10),(0,-10)]},
            'rk': {'frames': [278,279,280,281,280,279,278], 'offsets': [(0,0),(25,30),(35,40),(35,40),(35,40),(25,30),(10,25)]},
        }
        self.guards ={
            'air_guard'   :{'frames':[102,103],'offsets':[(0,0),(0,0)]},
            'ground_guard':{'frames':[79,79,80,81],'offsets':[(0,0),(0,0),(0,0),(0,0)]},
            'sit_guard'   :{'frames':[82,83,84],'offsets':[(0,0),(0,0),(0,0)]},
        }
        self.hitted_motions={
            'air_hitted'   :{'frames':[21,22,23,27],'offsets':[(0,0),(0,0),(0,0),(0,0)]},
            'middle_hitted':{'frames':[5,6,7,6,5],'offsets':[(0,0),(0,0),(0,0),(0,0),(0,0)]},
            'low_hitted'   :{'frames':[9,10,11,10,9],'offsets':[(0,0),(0,0),(0,0),(0,0),(0,0)]}
        }
        self.combo_motions={
            'combo_1':{'frames':[391,392,393,394]},
            'combo_2':{'frames':[395,396,397,398,399,400,401,402,403,404]},
            'combo_3':{'frames':[191,192,193,194,195,196,197]},
        }
        self.delXPos=0
        self.delYPos=0
    def draw_idle_by_frame_num(self,frame, x, y,face_dir):
        self.delXPos=0
        self.delYPos=0

        if frame==4:
            self.delXPos+=16 * -face_dir
        elif frame==5:
            self.delYPos+=16
            pass
        fx, fy, fw, fh = self.frame_list[self.idle_frame_start + frame]
        dw = fw * CHARACTER_WIDTH_SCALE
        dh = fh * CHARACTER_HEIGHT_SCALE

        if face_dir == -1:
            self.print_image.clip_draw(fx, fy, fw, fh, x + self.delXPos, y + self.delYPos,dw,dh)
        else:
            self.print_image.clip_composite_draw(fx, fy, fw, fh, 0, 'h', x + self.delXPos, y + self.delYPos, dw, dh)
        pass

    def draw_by_frame_num(self, frame_num, x, y, face_dir):
        fx, fy, fw, fh = self.frame_list[frame_num]
        dw = fw * CHARACTER_WIDTH_SCALE
        dh = fh * CHARACTER_HEIGHT_SCALE
        # 항상 오프셋 적용: delXPos에는 이미 x 방향 보정(= ox * -face_dir)을 넣어야 함
        sx = x + self.delXPos
        sy = y + self.delYPos
        if face_dir == -1:
            self.print_image.clip_draw(fx, fy, fw, fh, sx, sy,dw,dh)
        else:
            self.print_image.clip_composite_draw(fx, fy, fw, fh, 0, 'h', sx, sy, dw, dh)

    def draw_by_act_kind(self, act_start_frame, act_frames, frame, x, y, face_dir):
        fx, fy, fw, fh = self.frame_list[act_start_frame + frame]
        sx = x + self.delXPos
        sy = y + self.delYPos
        dw = fw * CHARACTER_WIDTH_SCALE
        dh = fh * CHARACTER_HEIGHT_SCALE
        if face_dir == -1:
            self.print_image.clip_draw(fx, fy, fw, fh, sx, sy)
        else:
            self.print_image.clip_composite_draw(fx, fy, fw, fh, 0, 'h', sx, sy, fw, fh)

    def draw_normal_attack(self, attack_key, frame_index, x, y, face_dir):
        info = self.normal_attacks.get(attack_key)
        if not info:
            return
        frames = info['frames']
        offsets = info.get('offsets', [(0, 0)] * len(frames))
        idx = max(0, min(frame_index, len(frames) - 1))
        frame_num = frames[idx]
        ox, oy = offsets[idx]
        # 방향에 따른 반전은 x좌표(ox)만 반영
        ox = ox * -face_dir
        self.delXPos = ox
        self.delYPos = oy
        # 재사용 가능한 기존 헬퍼 사용
        self.draw_by_frame_num(frame_num, x, y, face_dir)

    def draw_jump_attack(self, attack_key, frame_index, x, y, face_dir):
        info = self.jump_attacks.get(attack_key)
        if not info:
            return
        frames = info.get('frames', [])
        offsets = info.get('offsets', [(0, 0)] * len(frames))
        idx = max(0, min(frame_index, len(frames) - 1))
        frame_num = frames[idx]
        ox, oy = offsets[idx]
        # x만 방향 반영
        ox = ox * -face_dir
        self.delXPos = ox
        self.delYPos = oy
        # 기존 헬퍼 재사용
        self.draw_by_frame_num(frame_num, x, y, face_dir)

    def is_attack_finished(self, attack_key, frame_index):
        info = self.normal_attacks.get(attack_key)
        if not info:
            return True
        return frame_index >= (len(info['frames']) - 1)


class ShingoFrameInfo:
    pass

class LeonaFrameInfo:
    pass