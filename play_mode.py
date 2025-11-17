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

def update():
    # 이전 위치 저장
    for c in characters:
        c._prev_x = getattr(c, 'xPos', None)
        c._prev_y = getattr(c, 'yPos', None)

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
    # 내부 구조를 활용 (InteractionManager._hitboxes 로 최근 프레임 히트박스 리스트 사용)
    hbs = getattr(interaction_manager, '_hitboxes', [])
    n = len(hbs)

    def _is_attacking(owner):
        return bool(getattr(owner, 'is_attacking', False) or getattr(owner, 'attacking', False) or getattr(owner, 'is_attack', False))

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

            if not _is_attacking(A) and not _is_attacking(B):
                # 둘 다 공격중이 아니면 최소 침투축으로 서로 반씩 밀어냄
                if dx <= dy:
                    # x축 분리
                    cx_a = (l1 + r1) / 2.0
                    cx_b = (l2 + r2) / 2.0
                    shift = dx / 2.0
                    if cx_a < cx_b:
                        if hasattr(A, 'xPos'):
                            A.xPos -= shift
                        if hasattr(B, 'xPos'):
                            B.xPos += shift
                    else:
                        if hasattr(A, 'xPos'):
                            A.xPos += shift
                        if hasattr(B, 'xPos'):
                            B.xPos -= shift
                else:
                    # y축 분리
                    cy_a = (b1 + t1) / 2.0
                    cy_b = (b2 + t2) / 2.0
                    shift = dy / 2.0
                    if cy_a < cy_b:
                        if hasattr(A, 'yPos'):
                            A.yPos -= shift
                        if hasattr(B, 'yPos'):
                            B.yPos += shift
                    else:
                        if hasattr(A, 'yPos'):
                            A.yPos += shift
                        if hasattr(B, 'yPos'):
                            B.yPos -= shift
            else:
                # 공격 중이면 이전 위치로 축별 복원 시도 (이동한 주체만 복원)
                if dx <= dy:
                    moved_a_x = (getattr(A, '_prev_x', None) is not None and A._prev_x != getattr(A, 'xPos', None))
                    moved_b_x = (getattr(B, '_prev_x', None) is not None and B._prev_x != getattr(B, 'xPos', None))
                    if moved_a_x and not moved_b_x:
                        A.xPos = A._prev_x
                    elif moved_b_x and not moved_a_x:
                        B.xPos = B._prev_x
                    else:
                        if getattr(A, '_prev_x', None) is not None:
                            A.xPos = A._prev_x
                        if getattr(B, '_prev_x', None) is not None:
                            B.xPos = B._prev_x
                else:
                    moved_a_y = (getattr(A, '_prev_y', None) is not None and A._prev_y != getattr(A, 'yPos', None))
                    moved_b_y = (getattr(B, '_prev_y', None) is not None and B._prev_y != getattr(B, 'yPos', None))
                    if moved_a_y and not moved_b_y:
                        A.yPos = A._prev_y
                    elif moved_b_y and not moved_a_y:
                        B.yPos = B._prev_y
                    else:
                        if getattr(A, '_prev_y', None) is not None:
                            A.yPos = A._prev_y
                        if getattr(B, '_prev_y', None) is not None:
                            B.yPos = B._prev_y

            # 속도 보정: 위치 보정이 일어났으면 해당 축 속도 0으로
            EPS = 1e-6
            for owner in (A, B):
                prev_x = getattr(owner, '_prev_x', None)
                prev_y = getattr(owner, '_prev_y', None)
                cur_x = getattr(owner, 'xPos', getattr(owner, 'x', 0.0))
                cur_y = getattr(owner, 'yPos', getattr(owner, 'y', 0.0))

                # 공중 판정: ground_y가 있으면 yPos 비교 + vy 체크, 없으면 vy만 사용
                ground_y = getattr(owner, 'ground_y', getattr(owner, 'default_ground_y', None))
                vy_val = getattr(owner, 'vy', 0.0)
                if ground_y is not None:
                    airborne = (cur_y > ground_y + EPS) or (abs(vy_val) > EPS)
                else:
                    airborne = abs(vy_val) > EPS

                # x 축 보정이 있었다면 항상 vx를 0으로
                if prev_x is not None and abs(prev_x - cur_x) > EPS and hasattr(owner, 'vx'):
                    owner.vx = 0.0

                # y 축 보정이 있었다면 지상일 때만 vy를 0으로 (공중이면 유지)
                if prev_y is not None and abs(prev_y - cur_y) > EPS and hasattr(owner, 'vy'):
                    if not airborne:
                        owner.vy = 0.0


def draw():
    clear_canvas()
    game_world.render()
    if getattr(interaction_manager, 'show_hitboxes', False):
        interaction_manager.debug_draw()
    update_canvas()

def finish():
    game_world.clear()
    pass


