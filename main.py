from pico2d import *
import game_framework
import intro_mode as character_select_mode
import play_mode

open_canvas()
#game_framework.run(character_select_mode)
game_framework.run(play_mode)
close_canvas()