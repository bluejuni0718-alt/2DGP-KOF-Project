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
    def __init__(self,frame_list_path='CharacterSpriteSheet_Modified/Shingo_frame_box.png', print_image_path='CharacterSpriteSheet_Modified/Shingo_frames_alpha1.png'):
        self.frame_list = get_frame_list(frame_list_path)
        self.print_image = load_image(print_image_path)
        self.idle_frame_start= 0
        self.idle_frames = 6
        self.walk_frame_start = 8
        self.walk_frames = 6
        self.jump_frame_start = 20
        self.jump_frames = 4
        self.jump_move_motion_list = [20, 25, 26, 27, 28, 29, 30]
        self.jump_move_frame_start = 0
        self.jump_move_frames = 7
        self.run_frame_start= 168
        self.run_frames = 6
        self.back_dash_frame_start = 0
        self.sit_down_frame_start = 31
        self.sit_down_frames = 3
        self.dead_frame = 208
        #방향에 따른 공격값 -> face방향에 따라 반대면 배열의 뒤에서 부터 접근하기?
        self.normal_attacks = {
            'rp': {'frames': [274,275,276,277,278,279,280], 'offsets': [(0, 0), (8, 0), (0, 0)]},
            'lp': {'frames':[58,59],'offsets':[(0, 0), (8, 0), (0, 0)]},
            'lk': {'frames':[87,89,91,93,94,95],'offsets':[(0,0),(0,0),(-10,0),(0,0),(0,0)]},
            'rk': {'frames': [66,67,68,69,68], 'offsets': [(0, 0), (8, 0), (0, 0), (8, 0), (0, 0)]},
        }
        self.jump_attacks ={
            'rp': {'frames': [80, 81, 81,81,81], 'offsets': [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]},
            'lp': {'frames':[60,61,61,61],'offsets':[(0, 0), (0, 0), (0, 0)]},
            'lk': {'frames':[98,101,100,100],'offsets':[(0,0),(8,0),(0,0),(0,0)]},
            'rk': {'frames': [71,70,70,70], 'offsets': [(0, 0),(0, 0),  (0, 0)]},
        }
        self.move_jump_attacks={
            'rp': {'frames': [80, 81, 81,81,81], 'offsets': [(0, 0), (8, 0), (0, 0), (8, 0), (0, 0)]},
            'lp': {'frames':[60,61,61,61,61,61],'offsets':[(0, 0), (8, 0), (0, 0)]},
            'lk': {'frames':[98,101,100,100,100,100],'offsets':[(0,-20),(0,-20),(0,-20),(0,-20),(0,-20),(0,-20)]},
            'rk': {'frames':[71,72,72,72,72], 'offsets':[(0,0),(0,0),(0,0),(0,0)]},
        }
        self.sit_attacks = {
            'rp': {'frames':[64,65,64],'offsets':[(0,0),(20,-10),(0,0)]},
            'lp': {'frames':[32,79,78,77,78,79],'offsets':[(0,0),(0,0),(0,0), (0, 0), (0, 0), (0, 0)]},
            'lk': {'frames': [111,109,108,107,109], 'offsets': [(0,-10),(0,-10),(0,-10),(0,-10),(0,-10),(0,-10)]},
            'rk': {'frames': [73,74], 'offsets': [(0,0),(0,-20)]},
        }
        self.guards ={
            'air_guard'   :{'frames':[42,43],'offsets':[(0,0),(0,0)]},
            'ground_guard':{'frames':[44,45,46,45,44],'offsets':[(0,0),(0,0),(0,0),(0,0)]},
            'sit_guard'   :{'frames':[47,48,49,48,47],'offsets':[(0,0),(0,0),(0,0)]},
        }
        self.hitted_motions={
            'air_hitted'   :{'frames':[21,22,23,27],'offsets':[(0,0),(0,0),(0,0),(0,0)]},
            'middle_hitted':{'frames':[44,45,46,45,44],'offsets':[(0,0),(0,0),(0,0),(0,0),(0,0)]},
            'low_hitted'   :{'frames':[47,48,49,48,47],'offsets':[(0,0),(0,0),(0,0),(0,0),(0,0)]}
        }
        self.combo_motions={
            'combo_1':{'frames':[114,114,115,115,115]},
            'combo_2':{'frames':[129,130,131,132,133,134]},
            'combo_3':{'frames':[144,145,146,147,148,149,150]},
        }
        self.delXPos=0
        self.delYPos=0
    def draw_idle_by_frame_num(self,frame, x, y,face_dir):
        self.delXPos=0
        self.delYPos=0

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

#0, 53
class YuriFrameInfo:
    def __init__(self, frame_list_path='CharacterSpriteSheet_Modified/Yuri_frame_box.png',
                 print_image_path='CharacterSpriteSheet_Modified/Yuri_frames_alpha1.png'):
        self.frame_list = get_frame_list(frame_list_path)
        self.print_image = load_image(print_image_path)
        self.idle_frame_start = 0
        self.idle_frames = 6
        self.walk_frame_start = 290
        self.walk_frames = 4
        self.jump_frame_start = 24
        self.jump_frames = 5
        self.jump_move_motion_list = [24, 25, 26, 30, 31, 32, 33]
        self.jump_move_frame_start = 0
        self.jump_move_frames = 7
        self.run_frame_start = 44
        self.run_frames = 6
        self.back_dash_frame_start = 50
        self.sit_down_frame_start = 15
        self.sit_down_frames = 3
        self.dead_frame = 174
        # 방향에 따른 공격값 -> face방향에 따라 반대면 배열의 뒤에서 부터 접근하기?
        self.normal_attacks = {
            'rp': {'frames': [105, 106, 107], 'offsets': [(0, 0), (8, 0), (0, 0)]},
            'lp': {'frames': [79,80,79], 'offsets': [(0, 0), (0, 0), (0, 0)]},
            'lk': {'frames': [93,91,93], 'offsets': [(0, 0), (0, 0), (0, 0)]},
            'rk': {'frames': [118,119,120,121,122,123], 'offsets': [(0, 0), (8, 0), (0, 0), (8, 0), (0, 0), (0, 0)]},
        }
        self.jump_attacks = {
            'rp': {'frames': [108,109,110,110,110], 'offsets': [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]},
            'lp': {'frames': [81,82,83,83], 'offsets': [(0, 0), (0, 0), (0, 0), (0, 0)]},
            'lk': {'frames': [125,126,127,127,127], 'offsets': [(0, 0),(0, 0), (8, 0), (0, 0), (0, 0)]},
            'rk': {'frames': [279,278,278,278], 'offsets': [(0, 0),(0, 0), (0, 0), (0, 0)]},
        }
        self.move_jump_attacks = {
            'rp': {'frames': [108,109,110,110,110], 'offsets': [(0, 0), (8, 0), (0, 0), (8, 0), (0, 0)]},
            'lp': {'frames': [81,82,83,83], 'offsets': [(0, 0), (8, 0), (0, 0), (0, 0)]},
            'lk': {'frames': [125,126,127,127,127],
                   'offsets': [(0, -20), (0, -20), (0, -20), (0, -20), (0, -20), (0, -20)]},
            'rk': {'frames': [279,278,278,278], 'offsets': [(0, 0), (0, 0), (0, 0), (0, 0)]},
        }
        self.sit_attacks = {
            'rp': {'frames': [111,112,113,112], 'offsets': [(0, 0), (0, 10), (0, 20),(0, 10)]},
            'lp': {'frames': [84,85,84], 'offsets': [(0,0), (20,0), (0,0)]},
            'lk': {'frames': [96,97,96],
                   'offsets': [(0, -10), (0, -10), (0, -10), (0, -10), (0, -10), (0, -10)]},
            'rk': {'frames': [129,130,131,132,133,134],
                   'offsets': [(0, 0), (0,0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]},
        }
        self.guards = {
            'air_guard': {'frames': [36,37], 'offsets': [(0, 0), (0, 0)]},
            'ground_guard': {'frames': [30,61,62,63], 'offsets': [(0, 0), (0, 0), (0, 0), (0, 0)]},
            'sit_guard': {'frames': [36,37,37], 'offsets': [(0, 0), (0, 0), (0, 0)]},
        }
        self.hitted_motions = {
            'air_hitted': {'frames': [162,163,173,174], 'offsets': [(0, 0), (0, 0), (0, 0), (0, 0)]},
            'middle_hitted': {'frames': [142,143,144,143,142], 'offsets': [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]},
            'low_hitted': {'frames': [142,143,144,143,142], 'offsets': [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]}
        }
        self.combo_motions = {
            'combo_1': {'frames': [212,213,214,215,216]},
            'combo_2': {'frames': [217,218,219,212,213,214,215,216,217,218]},
            'combo_3': {'frames': [218,219,212,222,223]},
        }
        self.delXPos = 0
        self.delYPos = 0

    def draw_idle_by_frame_num(self, frame, x, y, face_dir):
        self.delXPos = 0
        self.delYPos = 0


        fx, fy, fw, fh = self.frame_list[self.idle_frame_start + frame]
        dw = fw * CHARACTER_WIDTH_SCALE
        dh = fh * CHARACTER_HEIGHT_SCALE

        if face_dir == -1:
            self.print_image.clip_draw(fx, fy, fw, fh, x + self.delXPos, y + self.delYPos, dw, dh)
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
            self.print_image.clip_draw(fx, fy, fw, fh, sx, sy, dw, dh)
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