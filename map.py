from matplotlib.pyplot import margins
from pico2d import load_image, get_canvas_width, get_canvas_height, clamp
import common
import game_framework

class PalaceMap:
    def __init__(self, margin = 50):
        self.image = load_image('GameMode_image/Game_Play_Map.png')
        self.cw = get_canvas_width()
        self.ch = get_canvas_height()
        self.w = self.image.w
        self.h = self.image.h
        self.margin = margin
        self.window_left = 0
        self.window_bottom = 0

    def update(self):
        p1 = common.characters[0]
        p2 = common.characters[1]

        if p1.xPos < p2.xPos:
            left, right = p1, p2
        else:
            left, right = p2, p1

        #오른쪽으로 벗어나려 할 경우
        if right.xPos > self.cw + self.window_left:# and right.back_pressed == True:
            if left.xPos > self.window_left + self.margin * 2:
                self.window_left = clamp(0, int(right.xPos - self.cw), self.w - self.cw)
                right.xPos = clamp(0, right.xPos, self.w -1)
            else:
                right.xPos = clamp(0, right.xPos, self.cw + self.window_left - 1)
        #왼쪽으로 벗어나려 할 경우
        elif  left.xPos < self.window_left + 2*self.margin:# and left.back_pressed == True:
            if right.xPos < self.cw + self.window_left:
                self.window_left = clamp(0, int(left.xPos - 2*self.margin), self.w - self.cw)
                left.xPos = clamp(self.window_left + 2*self.margin, left.xPos, self.w - self.margin - 1)
            else:
                left.xPos = clamp(self.window_left + 2*self.margin, left.xPos, self.w -1)


    def draw(self):
        self.image.clip_draw_to_origin(
            self.window_left,
            self.window_bottom,
            self.cw,
            self.ch, 0, 0
        )


class Timer:
    def __init__(self):
        self.total_time = 0.0
        self.image = load_image('GameMode_image/Game_Play_Timer_alpha1.png')

    def update(self):
        self.total_time += game_framework.frame_time

    def draw(self):
        seconds = 60 - int(self.total_time) % 60
        ten = seconds // 10
        one = seconds % 10
        self.image.clip_draw(ten * 20, 51 ,19, 50, 390, 565, 30, 70)
        self.image.clip_draw(one * 20, 51, 19, 50, 420,565,30,70)

class HpBar:
    def __init__(self, character, x, y):
        self.character = character
        self.x = x
        self.y = y
        self.Hp_Bar_image = load_image('GameMode_image/Game_Play_HPbar.png')
        self.Hp_Bar_Cover_image = load_image('GameMode_image/Game_Play_HPbar_Cover.png')

    def update(self):
        pass

    def draw(self):
        self.Hp_Bar_Cover_image.clip_draw(0, 0, 100, 40, self.x, self.y, 300, 40)
        self.Hp_Bar_image.clip_draw(0, 0, 300, 40, self.x - 3*(100 - self.character.hp)/2, self.y, 3 * self.character.hp, 40)

class WinCount:
    def __init__(self, character, x, y):
        self.character = character
        self.x = x
        self.y = y
        self.Win_Count_1_image = load_image('GameMode_image/Game_Play_Win_Count.png')
        self.Win_Count_2_image = load_image('GameMode_image/Game_Play_Win_Count.png')

    def update(self):
        pass

    def draw(self):
        if self.character.win_count == 0:
            self.Win_Count_1_image.clip_draw(0, 0, 30, 30, self.x, self.y, 30, 30)
            self.Win_Count_2_image.clip_draw(0, 0, 30, 30, self.x + 30, self.y, 30, 30)
        elif self.character.win_count ==1:
            self.Win_Count_1_image.clip_draw(0, 0, 30, 30, self.x, self.y, 30, 30)
            self.Win_Count_2_image.clip_draw(30, 0, 30, 30, self.x + 30, self.y, 30, 30)
        elif self.character.win_count ==2:
            self.Win_Count_1_image.clip_draw(30, 0, 30, 30, self.x, self.y, 30, 30)
            self.Win_Count_2_image.clip_draw(30, 0, 30, 30, self.x + 30, self.y, 30, 30)



