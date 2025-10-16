from pico2d import *
from frame import *

open_canvas()
test_image = load_image('CharacterSpriteSheet_Modified\Kim_frames_alpha1.png')

frame_list = get_frame_list('CharacterSpriteSheet_Modified\Kim_frame_box.png')
#for frame in frame_list:
#   print(frame)

frame_num = 0

while True:
    clear_canvas()
    events = get_events()
    for event in events:
        if event.type==SDL_KEYDOWN:
            if event.key == SDLK_LEFT:
                frame_num -= 1
            elif event.key == SDLK_RIGHT:
                frame_num += 1
    test_image.clip_draw(frame_list[frame_num][0], frame_list[frame_num][1], frame_list[frame_num][2], frame_list[frame_num][3], 400, 200)
    update_canvas()
    pass
close_canvas()
