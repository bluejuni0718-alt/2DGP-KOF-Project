from pico2d import *
from frame import *

open_canvas()
test_image = load_image('CharacterSpriteSheet_Modified\Kim_frame_box.png')

frame_list = get_frame_list('CharacterSpriteSheet_Modified\Kim_frame_box.png')
for frame in frame_list:
   print(frame)



close_canvas()
