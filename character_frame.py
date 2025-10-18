from pico2d import *
from frame import *

class KimFrameInfo:
    def __init__(self,frame_list_path='CharacterSpriteSheet_Modified/Kim_frame_box.png', print_image_path='CharacterSpriteSheet_Modified/Kim_frames_alpha1.png'):
        self.frame_list = get_frame_list(frame_list_path)
        self.print_image = load_image(print_image_path)
        self.idle_frame_start= 307
        self.idle_frames = 6
        self.delXPos=0
        self.delYPos=0
        pass
    def draw_by_frame_num(self,frame_num, x,y,scale_x=None,scale_y=None):
        fx,fy,fw,fh=self.frame_list[frame_num]
        self.print_image.clip_draw(fx, fy, fw, fh, x, y,scale_x, scale_y)
        pass
    def draw_by_frame_num_composite(self,frame_num,x,y,scale_x=None,scale_y=None):
        fx,fy,fw,fh=self.frame_list[frame_num]
        self.print_image.clip_composite_draw(fx,fy,fw,fh,0,'h',x,y,scale_x, scale_y)
        pass
    def draw_idle_by_frame_num(self,frame,x,y):
        pass