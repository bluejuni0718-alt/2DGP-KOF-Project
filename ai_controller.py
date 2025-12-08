from behavior_tree import BehaviorTree, Selector, Sequence, Condition, Action
from types import SimpleNamespace
from pico2d import *
from random import randint

class AIController:
    def __init__(self, character, target):
        self.ch = character
        self.target = target
        self.now_key = None
        self.bt = self.build_behavior_tree()
    def update(self):
        self.bt.run()

    def run(self):
        self.update()

    def distance_less_than_50(self):
        distance = abs(self.ch.xPos - self.target.xPos)
        return distance < 100

    def if_target_nearby(self):
        if self.distance_less_than_50():
            return BehaviorTree.FAIL
        else:
            return BehaviorTree.SUCCESS

    def if_target_dead(self):
        if self.target.hp<=0:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def can_attack_target(self):
        if self.distance_less_than_50():
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def is_get_hitted(self):
        if self.ch.is_hitted:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def get_damaged(self):
        self.become_idle()
        e = ('HITTED',None)
        self.ch.state_machine.handle_state_event(e)
        return BehaviorTree.SUCCESS

    def get_event_percentage(self, percent):
        action_num = randint(0,1000)
        if action_num < percent:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def jump(self):
        e = ('INPUT',SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['up']))
        self.ch.state_machine.handle_state_event(e)

    def guard(self):
        if self.ch.face_dir == 1:
            e = ('INPUT',SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['right']))
        else:
            e = ('INPUT',SimpleNamespace(type=SDL_KEYDOWN,key=self.ch.keymap['left']))
        self.ch.state_machine.handle_state_event(e)

    def attack_target(self):
        attack_num = randint(0,4)
        if attack_num == 0:
            e = ('INPUT',SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['rk']))
        elif attack_num == 1:
            e = ('INPUT',SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['lk']))
        elif attack_num == 2:
            e = ('INPUT',SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['rp']))
        else:
            e = ('INPUT',SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['lp']))
        self.ch.state_machine.handle_state_event(e)

    def move_towards_target(self):
        if self.ch.face_dir == 1:
            e = ('INPUT',SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['left']))
        else:
            e = ('INPUT',SimpleNamespace(type=SDL_KEYDOWN,key=self.ch.keymap['right']))
        self.ch.state_machine.handle_state_event(e)

    def move_to_target(self):
        if self.ch.face_dir == -1:
            e = ('INPUT',SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['left']))
        else:
            e = ('INPUT',SimpleNamespace(type=SDL_KEYDOWN,key=self.ch.keymap['right']))
        self.ch.state_machine.handle_state_event(e)
        if self.distance_less_than_50:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING

    def become_idle(self):
        e = ('INPUT', SimpleNamespace(type=SDL_KEYUP, key=self.ch.keymap['left']))
        self.ch.state_machine.handle_state_event(e)
        e = ('INPUT', SimpleNamespace(type=SDL_KEYUP, key=self.ch.keymap['right']))
        self.ch.state_machine.handle_state_event(e)
        return BehaviorTree.SUCCESS

    def build_behavior_tree(self):
        # Conditions
        c_is_nearby = Condition('타겟이 근처에 있는가?', self.if_target_nearby)
        c_can_attack = Condition('타겟을 공격할 수 있는가?', self.can_attack_target)
        c_is_hitted = Condition('피격 당했는가?', self.is_get_hitted)
        c_jump_percent = Condition('점프 확률 검사', lambda: self.get_event_percentage(2))
        c_guard_percent = Condition('가드 확률 검사', lambda: self.get_event_percentage(3))
        c_is_target_dead = Condition('타겟이 죽었는가?', self.if_target_dead)
        # Actions
        a_trace_target = Action('타겟에게 다가가기', self.move_to_target)
        a_to_be_idle = Action('대기 상태가 되기', self.become_idle)
        a_attack_target = Action('타겟 공격하기', self.attack_target)
        a_get_damaged = Action('피격 당하기', self.get_damaged)
        a_jump = Action('점프하기', self.jump)
        a_guard = Action('가드하기', self.guard)
        # Sequences
        s_trace_target = Sequence('타겟 추적 시퀀스', c_is_nearby, a_trace_target)
        s_attack_target = Sequence('타겟 공격 시퀀스', c_can_attack, a_attack_target)
        s_get_damaged = Sequence('피격 시퀀스', c_is_hitted, a_get_damaged)
        s_jump = Sequence('점프 시퀀스', c_jump_percent, a_jump)
        s_guard = Sequence('가드 시퀀스', c_guard_percent, a_guard)
        s_target_dead = Sequence('타겟 사망 시퀀스', c_is_target_dead, a_to_be_idle)
        root = Selector('루트 셀렉터',  s_target_dead, s_get_damaged,s_jump,s_guard,s_trace_target,s_attack_target,a_to_be_idle)

        return BehaviorTree(root)