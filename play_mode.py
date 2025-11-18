from pico2d import *
import game_framework
from character import Character, KimFrameInfo
import game_world
import intro_mode
from interaction import *

def pico_renderer(left, bottom, right, top, color=None, tag=None):
    # 간단히 사각형 외곽을 그림. color/tag는 무시하거나 확장 가능.
    draw_rectangle(left, bottom, right, top)

interaction_manager = InteractionManager(renderer=pico_renderer)

interaction_manager.show_hitboxes = True

running = True
characters =[]
KEYMAP_P1 ={
    'left' :SDLK_a,
    'right':SDLK_d,
    'up'   :SDLK_w,
    'down' :SDLK_s,
    'lp'   :SDLK_f,
    'rp'   :SDLK_g,
    'rk'   :SDLK_b,
    'lk'   :SDLK_c
}
KEYMAP_P2 ={
    'left'  :SDLK_LEFT,
    'right' :SDLK_RIGHT,
    'up'    :SDLK_UP,
    'down'  :SDLK_DOWN,
    'lp'    :SDLK_KP_4,
    'rp'    :SDLK_KP_5,
    'rk'    :SDLK_KP_2,
    'lk'    :SDLK_KP_1
}


def handle_events():
    event_list = get_events()
    global running
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        elif event.type==SDL_KEYDOWN and event.key==SDLK_r:
            game_framework.change_mode(intro_mode)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_h:
            # H 키로 히트박스 토글
            interaction_manager.show_hitboxes = not getattr(interaction_manager, 'show_hitboxes', True)
        else:
            for c in characters:
                c.handle_event(event)
    pass

def init():
    global characters
    c1 = Character(KimFrameInfo(), keymap=KEYMAP_P1, manager=interaction_manager, x=100, y=120)
    c2 = Character(KimFrameInfo(), keymap=KEYMAP_P2, manager=interaction_manager, x=400, y=120)
    characters = [c1, c2]
    if c1.xPos < c2.xPos:
        c1.face_dir = 1
        c2.face_dir = -1
    else:
        c1.face_dir = -1
        c2.face_dir = 1

    for c in characters:
        game_world.add_object(c)

# python
def update():
    # 이전 위치 저장
    for c in characters:
        try:
            c._prev_xPos = getattr(c, 'xPos', 0.0)
            c._prev_yPos = getattr(c, 'yPos', 0.0)
        except Exception:
            pass

    # 게임 로직 업데이트(위치 등 변경)
    game_world.update()

    # 히트박스 수집/판정 준비
    interaction_manager.begin_frame()
    for c in characters:
        try:
            c.register_hitboxes()
        except Exception:
            pass

    # 충돌 이벤트 발생 (enter/stay/exit)
    interaction_manager.process()

    # 충돌 해소: 등록된 히트박스 쌍을 순회하여 겹침 보정
    hbs = getattr(interaction_manager, '_hitboxes', [])
    n = len(hbs)

    def _is_attacking(owner):
        return bool(getattr(owner, 'is_attacking', False))

    EPS = 1e-6

    for i in range(n):
        a = hbs[i]
        for j in range(i + 1, n):
            b = hbs[j]
            if a.owner is b.owner:
                continue

            l1, b1, r1, t1 = a.as_bbox()
            l2, b2, r2, t2 = b.as_bbox()

            # 침투량 계산
            dx = min(r1, r2) - max(l1, l2)
            dy = min(t1, t2) - max(b1, b2)
            if dx <= 0 or dy <= 0:
                continue

            A = a.owner
            B = b.owner

            # (필요하면 공격 관련 예외처리 여기에 추가)
            # if not _is_attacking(A) and not _is_attacking(B):
            #     ...

            # 위치 보정 플래그 (축별로 속도 0 처리에 사용)
            moved_x_A = moved_x_B = moved_y_A = moved_y_B = False

            # 수평 분리 (dx < dy)
            if dx < dy:
                # 중심 기준으로 어느 쪽으로 밀어낼지 결정
                cx1 = (l1 + r1) / 2.0
                cx2 = (l2 + r2) / 2.0
                push = dx
                # 양쪽을 반반씩 밀어서 자연스럽게 분리
                half = push / 2.0
                if cx1 < cx2:
                    try:
                        A.xPos -= half
                        moved_x_A = True
                    except Exception:
                        pass
                    try:
                        B.xPos += half
                        moved_x_B = True
                    except Exception:
                        pass
                else:
                    try:
                        A.xPos += half
                        moved_x_A = True
                    except Exception:
                        pass
                    try:
                        B.xPos -= half
                        moved_x_B = True
                    except Exception:
                        pass

            else:
                # vertical separation
                cy1 = (b1 + t1) / 2.0
                cy2 = (b2 + t2) / 2.0

                if cy1 > cy2:
                    top_owner, top_bbox = A, (l1, b1, r1, t1)
                    bot_owner, bot_bbox = B, (l2, b2, r2, t2)
                else:
                    top_owner, top_bbox = B, (l2, b2, r2, t2)
                    bot_owner, bot_bbox = A, (l1, b1, r1, t1)

                l_top, b_top, r_top, t_top = top_bbox
                l_bot, b_bot, r_bot, t_bot = bot_bbox

                # horizontal overlap amount
                overlap_x = max(0.0, min(r_top, r_bot) - max(l_top, l_bot))
                bot_width = max(EPS, (r_bot - l_bot))

                # airborne 판정
                vy_top = getattr(top_owner, 'vy', 0.0)
                ground_y_top = getattr(top_owner, 'ground_y', getattr(top_owner, 'default_ground_y', None))
                if ground_y_top is not None:
                    airborne_top = (getattr(top_owner, 'yPos', 0.0) > ground_y_top + EPS) or (abs(vy_top) > EPS)
                else:
                    airborne_top = abs(vy_top) > EPS

                # 위에서 아래로 내려오면서 아래의 절반 이상 겹치면 통과 허용
                if airborne_top and vy_top < 0.0 and (overlap_x >= 0.5 * bot_width):
                    # 통과: 아무 보정도 하지 않음
                    pass
                else:
                    # 차단: 위 캐릭터만 위로 올려 착지 처리 (아래 캐릭터의 y/ground는 변경하지 않음)
                    penetration_y = dy
                    try:
                        top_owner.yPos += penetration_y
                        moved_y_top = True
                    except Exception:
                        pass

                    try:
                        # 착지 기준은 아래 히트박스의 top으로 설정
                        top_owner.ground_y = t_bot
                    except Exception:
                        pass

                    # 착지이므로 위 캐릭터의 vy만 정리
                    if hasattr(top_owner, 'vy'):
                        top_owner.vy = 0.0

                    # 아래 캐릭터를 아래로 밀지 않고 옆으로 밀어 분리
                    try:
                        cx_top = (l_top + r_top) / 2.0
                        cx_bot = (l_bot + r_bot) / 2.0
                        dir_sign = 1.0 if cx_top < cx_bot else -1.0
                        # 밀어낼 양: 최소 1픽셀 보장, 겹침의 절반 정도
                        push_amount = max(1.0, overlap_x / 2.0)
                        if hasattr(bot_owner, 'xPos'):
                            bot_owner.xPos += dir_sign * push_amount
                            # bot_owner가 옆으로 이동했으므로 x 속도 보정 가능
                            if hasattr(bot_owner, 'vx'):
                                bot_owner.vx = 0.0
                    except Exception:
                        pass

            # 속도 보정: 위치 보정이 일어났으면 해당 축 속도 0으로
            try:
                if moved_x_A and hasattr(A, 'vx'):
                    A.vx = 0.0
                if moved_x_B and hasattr(B, 'vx'):
                    B.vx = 0.0
                if moved_y_A and hasattr(A, 'vy'):
                    A.vy = 0.0
                if moved_y_B and hasattr(B, 'vy'):
                    B.vy = 0.0
            except Exception:
                pass


def draw():
    clear_canvas()
    game_world.render()
    if getattr(interaction_manager, 'show_hitboxes', False):
        interaction_manager.debug_draw()
    update_canvas()

def finish():
    game_world.clear()
    pass


