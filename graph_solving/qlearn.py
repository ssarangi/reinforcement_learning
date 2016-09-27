class QLearner:
    def __init__(self, model_size, gamma):
        size = model_size
        self.Q = [[0] * size for _ in range(0, size)]
        self.gamma = gamma
        self.start = -1
        self.goal = -1
        self.current_state = -1

    def set_start_and_goal(self, start, goal):
        self.start = start
        self.goal = goal
        self.current_state = start

    def update_current_state(self, state):
        self.current_state = state

    def execute_step(self, next_state, next_state_actions, reward_matrix):
        next_state_action_Q = 0

        for i in range(0, len(next_state_actions)):
            next_state_action_Q = max(next_state_action_Q, self.Q[next_state][next_state_actions[i]])

        self.Q[self.current_state][next_state] = reward_matrix[self.current_state][next_state] + self.gamma * next_state_action_Q
        self.current_state = next_state

    def stop_training(self):
        self.gamma = 1.0

    def get_Q_value(self, current_state, next_state):
        return self.Q[current_state][next_state]