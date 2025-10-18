from event_to_string import event_to_string

class StateMachine:
    def __init__(self,start_state,state_transitions):
        self.cur_state=start_state
        self.state_transitions=state_transitions
        self.cur_state.enter(('START', None))
        pass

    def update(self):
        pass

    def handle_state_event(self, event):
        pass

    def draw(self):
        pass