from pico2d import *
from frame import *

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
        self.jump_move_motion_list = [97, 98, 153, 154, 155, 156, 100, 101]
        self.jump_move_frame_start = 0
        self.jump_move_frames = 8
        self.run_frame_start= 73
        self.run_frames = 6
        self.back_dash_frame_start = 378
        self.delXPos=0
        self.delYPos=0

        pass
    def draw_idle_by_frame_num(self,frame, x, y,face_dir):
        self.delXPos=0
        self.delYPos=0
        if frame==4:
            self.delXPos+=8 * face_dir
        elif frame==5:
            self.delYPos+=8
            pass
        fx, fy, fw, fh = self.frame_list[self.idle_frame_start + frame]
        if face_dir == -1:
            self.print_image.clip_draw(fx, fy, fw, fh, x + self.delXPos, y + self.delYPos)
        else:
            self.print_image.clip_composite_draw(fx, fy, fw, fh, 0, 'h', x + self.delXPos, y + self.delYPos, fw, fh)
        pass
    def draw_by_frame_num(self,frame_num,x, y,face_dir):
        fx, fy, fw, fh = self.frame_list[frame_num]
        if face_dir ==-1:
            self.print_image.clip_draw(fx, fy, fw, fh, x, y)
        else:
            self.print_image.clip_composite_draw(fx, fy, fw, fh, 0, 'h', x + self.delXPos, y + self.delYPos, fw, fh)
    def draw_by_act_kind(self,act_start_frame,act_frames,frame,x,y,face_dir):
        fx, fy, fw, fh = self.frame_list[act_start_frame + frame]
        if face_dir ==-1:
            self.print_image.clip_draw(fx, fy, fw, fh, x, y)
        else:
            self.print_image.clip_composite_draw(fx, fy, fw, fh, 0, 'h', x + self.delXPos, y + self.delYPos, fw, fh)
