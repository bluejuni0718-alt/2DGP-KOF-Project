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
    # 이전 위치/속도 저장 (간단한 디버깅/복원 용도)
    for c in characters:
        try:
            c._prev_pos = (getattr(c, 'xPos', 0.0), getattr(c, 'yPos', 0.0))
            c._prev_vel = (getattr(c, 'vx', 0.0), getattr(c, 'vy', 0.0))
        except Exception:
            pass

    # 게임 로직 업데이트
    try:
        game_world.update()
    except Exception:
        pass

    # 히트박스 수집/등록
    interaction_manager.begin_frame()
    for c in characters:
        try:
            c.register_hitboxes()
        except Exception:
            pass

    # 충돌 이벤트 발생
    try:
        interaction_manager.process()
    except Exception:
        pass

    # 충돌 해소: 등록된 히트박스 쌍을 순회하여 겹침 보정
    hbs = getattr(interaction_manager, '_hitboxes', [])
    n = len(hbs)

    def _is_attacking(owner):
        try:
            return bool(getattr(owner, 'is_attacking', False))
        except Exception:
            return False

    EPS = 1e-6

    for i in range(n):
        a = hbs[i]
        for j in range(i + 1, n):
            b = hbs[j]
            if a.owner is b.owner:
                continue

            try:
                l1, b1, r1, t1 = a.as_bbox()
                l2, b2, r2, t2 = b.as_bbox()
            except Exception:
                continue

            # 침투량 계산 (x, y)
            dx = min(r1, r2) - max(l1, l2)
            dy = min(t1, t2) - max(b1, b2)
            if dx <= 0 or dy <= 0:
                continue

            try:
                a_tag = getattr(a, 'tag', None)
                b_tag = getattr(b, 'tag', None)
                a_attacking = getattr(getattr(a, 'owner', None), 'is_attacking', False)
                b_attacking = getattr(getattr(b, 'owner', None), 'is_attacking', False)
                if (a_tag == 'attack' and a_attacking) or (b_tag == 'attack' and b_attacking):
                    # 공격 히트박스가 포함된 충돌은 연출을 위해 위치/속도 보정 없이 그대로 둠
                    continue
            except Exception:
                # 안전하게 넘어감(기존 로직 계속)
                pass

            A = a.owner
            B = b.owner

            # 위치 보정 플래그
            moved_x_A = moved_x_B = moved_y_A = moved_y_B = False

            # 수평 분리 (x 축 보정)
            if dx < dy:
                try:
                    cx1 = (l1 + r1) / 2.0
                    cx2 = (l2 + r2) / 2.0
                    shift = (dx / 2.0) + EPS
                    if cx1 < cx2:
                        # A 왼쪽, B 오른쪽 -> A를 왼쪽으로, B를 오른쪽으로 밀어 분리
                        if hasattr(A, 'xPos'):
                            A.xPos -= shift
                            moved_x_A = True
                        if hasattr(B, 'xPos'):
                            B.xPos += shift
                            moved_x_B = True
                    else:
                        # A 오른쪽, B 왼쪽 -> A를 오른쪽으로, B를 왼쪽으로 밀어 분리
                        if hasattr(A, 'xPos'):
                            A.xPos += shift
                            moved_x_A = True
                        if hasattr(B, 'xPos'):
                            B.xPos -= shift
                            moved_x_B = True
                except Exception:
                    pass

            else:
                # vertical separation (y 축 보정 우선)
                try:
                    cy1 = (b1 + t1) / 2.0
                    cy2 = (b2 + t2) / 2.0
                    # 위/아래 결정: cy가 큰 쪽이 위
                    if cy1 > cy2:
                        top_owner = A
                        bot_owner = B
                        l_top, b_top, r_top, t_top = l1, b1, r1, t1
                        l_bot, b_bot, r_bot, t_bot = l2, b2, r2, t2
                    else:
                        top_owner = B
                        bot_owner = A
                        l_top, b_top, r_top, t_top = l2, b2, r2, t2
                        l_bot, b_bot, r_bot, t_bot = l1, b1, r1, t1

                    # 속도/airborne 판정
                    vy_top = getattr(top_owner, 'vy', 0.0)
                    vy_bot = getattr(bot_owner, 'vy', 0.0)
                    ground_y_top = getattr(top_owner, 'ground_y', getattr(top_owner, 'default_ground_y', None))
                    ground_y_bot = getattr(bot_owner, 'ground_y', getattr(bot_owner, 'default_ground_y', None))

                    airborne_top = True
                    airborne_bot = True
                    try:
                        if ground_y_top is not None:
                            if getattr(top_owner, 'yPos', 0.0) <= ground_y_top + EPS and vy_top <= 0.0:
                                airborne_top = False
                    except Exception:
                        airborne_top = True
                    try:
                        if ground_y_bot is not None:
                            if getattr(bot_owner, 'yPos', 0.0) <= ground_y_bot + EPS and vy_bot <= 0.0:
                                airborne_bot = False
                    except Exception:
                        airborne_bot = True

                    # 마주보기 설정: 중심 x 기준 (x가 더 작으면 1, 더 크면 -1)
                    cx_top = (l_top + r_top) / 2.0
                    cx_bot = (l_bot + r_bot) / 2.0
                    top_should_face = 1 if cx_top < cx_bot else -1
                    bot_should_face = -top_should_face

                    # 즉시 또는 지연 적용 (공중이면 _deferred_facing에 저장)
                    def _apply_or_defer_facing(owner, desired_dir, airborne):
                        try:
                            if owner is None:
                                return
                            if airborne:
                                setattr(owner, '_deferred_facing', desired_dir)
                            else:
                                owner.face_dir = desired_dir
                                # 지상에서 즉시 적용하면 지연값 제거
                                if hasattr(owner, '_deferred_facing'):
                                    owner._deferred_facing = None
                        except Exception:
                            pass

                    _apply_or_defer_facing(top_owner, top_should_face, airborne_top)
                    _apply_or_defer_facing(bot_owner, bot_should_face, airborne_bot)

                    # 위에서 내려오는 경우(음의 vy)이고 아래의 너비 절반 이상 겹치면 통과 허용
                    overlap_x = min(r_top, r_bot) - max(l_top, l_bot)
                    bot_width = (r_bot - l_bot) if (r_bot - l_bot) > 0 else 0.0
                    allow_pass_through = False
                    try:
                        # 공격 히트박스 통과 허용:
                        # 한쪽 히트박스가 tag == 'attack' 이고 그 소유자가 is_attacking 이면 통과 허용
                        try:
                            if (getattr(a, 'tag', None) == 'attack' and getattr(a.owner, 'is_attacking', False)) or \
                                    (getattr(b, 'tag', None) == 'attack' and getattr(b.owner, 'is_attacking', False)):
                                allow_pass_through = True
                        except Exception:
                            # 안전하게 아무 변경 없이 진행
                            pass

                        # 기존 속도/겹침 기반 통과 판정은 공격 판정이 아닐 때만 적용
                        if not allow_pass_through:
                            try:
                                # 기존 로직에서 사용하던 vy_top, bot_width, overlap_x 변수를 그대로 사용
                                if getattr(top_owner, 'vy', 0.0) < 0.0 and bot_width > 0.0:
                                    if overlap_x >= (bot_width * 0.5):
                                        allow_pass_through = True
                            except Exception:
                                allow_pass_through = False
                    except Exception:
                        allow_pass_through = False

                    if allow_pass_through:
                        # 통과 허용: 위치 보정하지 않음
                        pass
                    else:
                        # 통상적인 수직 분리: 위를 위로, 아래를 아래로 밀어 분리
                        shift_y = (dy / 2.0) + EPS
                        # 위쪽을 위로
                        try:
                            top_owner.yPos += shift_y
                            moved_y_top = True
                        except Exception:
                            moved_y_top = False
                        # 아래쪽을 아래로 (되도록 지면 기준은 건드리지 않음)
                        try:
                            prev_bot_y = getattr(bot_owner, 'yPos', 0.0)
                            if ground_y_bot is not None:
                                new_bot_y = max(prev_bot_y - shift_y, ground_y_bot)
                            else:
                                new_bot_y = prev_bot_y - shift_y
                            bot_owner.yPos = new_bot_y
                            moved_y_bot = (new_bot_y != prev_bot_y)
                        except Exception:
                            moved_y_bot = False

                        # moved flags를 실제 A/B에 반영
                        if top_owner is A:
                            moved_y_A = bool(moved_y_top)
                            moved_y_B = bool(moved_y_bot)
                        else:
                            moved_y_A = bool(moved_y_bot)
                            moved_y_B = bool(moved_y_top)

                except Exception:
                    pass

            # 속도 보정: 위치 보정이 일어났으면 해당 축 속도 0으로
            try:
                if moved_x_A and hasattr(A, 'vx'):
                    try:
                        A.vx = 0.0
                    except Exception:
                        pass
                if moved_x_B and hasattr(B, 'vx'):
                    try:
                        B.vx = 0.0
                    except Exception:
                        pass
                if moved_y_A and hasattr(A, 'vy'):
                    try:
                        A.vy = 0.0
                    except Exception:
                        pass
                if moved_y_B and hasattr(B, 'vy'):
                    try:
                        B.vy = 0.0
                    except Exception:
                        pass
            except Exception:
                pass

    # 충돌 처리 후: 바닥 아래로 파고드는 것을 방지하기 위한 최종 클램프
    for c in characters:
        try:
            ground_y = getattr(c, 'ground_y', None)
            if ground_y is None:
                ground_y = getattr(c, 'default_ground_y', None)
            if ground_y is not None:
                if getattr(c, 'yPos', 0.0) < ground_y:
                    c.yPos = ground_y
                    if hasattr(c, 'vy') and getattr(c, 'vy', 0.0) < 0.0:
                        c.vy = 0.0
        except Exception:
            pass

    # 지연된 보는 방향 적용 (착지 시)
    for c in characters:
        try:
            df = getattr(c, '_deferred_facing', None)
            if df is None:
                continue
            # 이전 프레임 y (저장 안되어 있으면 현재보다 약간 위로 가정)
            prev_y = getattr(c, '_prev_pos', (0.0, getattr(c, 'yPos', 0.0)))[1]
            # 캐릭터의 기준 바닥(ground_y 또는 default_ground_y)
            ground_y = getattr(c, 'ground_y', None)
            if ground_y is None:
                ground_y = getattr(c, 'default_ground_y', getattr(c, 'yPos', 0.0))
            # 이전에는 공중(prev_y > ground_y)이고 현재는 착지(c.yPos <= ground_y)한 경우 적용
            if prev_y > ground_y and getattr(c, 'yPos', 0.0) <= ground_y:
                try:
                    c.face_dir = int(df)
                except Exception:
                    c.face_dir = 1 if df else -1
                c._deferred_facing = None
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


