class QLearner:
    def __init__(self, model_size, start, goal, gamma):
        size = model_size
        self.Q = [[0] * (size-1) for _ in range(0, size)]
        self.current_state = start
        self.goal = goal
        self.gamma = gamma

    def update_current_state(self, state):
        self.current_state = state

    def execute_step(self, next_state, next_state_actions, reward_matrix):
        next_state_action_Q = 0

        for i in range(0, len(next_state_actions)):
            next_state_action_Q = max(next_state_action_Q, self.Q[next_state][next_state_actions[i]])

        self.Q[self.current_state][next_state] = reward_matrix[self.current_state][next_state] + self.gamma * next_state_action_Q
        self.current_state = next_state