import networkx as nx
import matplotlib.pyplot as plt
import random
import pickle
import os
import sys

from qlearn import QLearner


class QLearnSolver:
    def __init__(self, num_nodes, start, goal, qlearner):
        self.num_nodes = num_nodes
        self.start = start
        self.goal = goal
        self.graph = nx.DiGraph()
        self.qlearner = qlearner

        assert 0 <= start <= num_nodes - 1
        assert 0 <= goal <= num_nodes - 1

        for i in range(0, num_nodes):
            self.graph.add_node(i)

        for i in range(0, num_nodes):
            n1 = random.randint(0, num_nodes - 1)
            n2 = random.randint(0, num_nodes - 1)
            if n1 == n2 or n1 in self.graph.neighbors(n2):
                continue
            self.graph.add_edge(n1, n2)

        # Make sure there is atleast one edge between the start and goal
        if start in self.graph.neighbors(goal):
            self.graph.remove_edge(goal, start)

        self.graph.add_edge(start, goal)

        # Create reward matrix
        self.reward_matrix = [[0] * (num_nodes) for _ in range(0, num_nodes)]

        goal_reward = 100
        for u, v in self.graph.edges():
            if v == goal:
                self.reward_matrix[u][v] = goal_reward

    def get_model_size(self):
        return self.num_nodes - 1

    def execute_training(self):
        self.qlearner.set_start_and_goal(self.start, self.goal)
        visited = {self.start}
        while self.qlearner.current_state != self.qlearner.goal:
            # From the current state figure out what are the possible next actions and select a random one
            actions = self.graph.neighbors(self.qlearner.current_state)

            # Check if all the actions have been visited or not.. If so then we have a cycle in
            # the graph
            all_actions_visited = True
            for action in actions:
                if action not in visited:
                    all_actions_visited = False

            if all_actions_visited:
                return

            if len(actions) == 0:
                return

            max_idx = len(actions)
            next_state = actions[random.randint(0, max_idx - 1)]
            if next_state in visited:
                continue
            else:
                visited.add(next_state)

            next_state_actions = self.graph.neighbors(next_state)
            self.qlearner.execute_step(next_state, next_state_actions, self.reward_matrix)

    def execute(self, trace=False):
        if trace:
            print("-" * 10 + " Execution tracing " + "-" * 10)
            print("Next State: %s" % self.start)
        self.qlearner.set_start_and_goal(self.start, self.goal)
        self.qlearner.stop_training()
        path = [self.qlearner.current_state]

        visited = {self.qlearner.current_state}

        while self.qlearner.current_state != self.qlearner.goal:
            actions = self.graph.neighbors(self.qlearner.current_state)

            if len(actions) == 0:
                return path

            next_state = actions[0]
            max_v = 0
            for action in actions:
                if action in visited:
                    continue
                visited.add(action)
                curr_v = self.qlearner.get_Q_value(self.qlearner.current_state, action)
                if curr_v > max_v:
                    next_state = action
                    max_v = curr_v

            if trace:
                print("Next State: %s Q Val: %s" % (next_state, max_v))

            path.append(next_state)
            self.qlearner.current_state = next_state

        if trace:
            print("-" * 10 + " Done Execution " + "-" * 10)

        return path

    def render(self):
        nodes = [i for i in range(0, self.num_nodes)]
        nodes.remove(self.start)
        nodes.remove(self.goal)

        pos = nx.shell_layout(self.graph)
        nx.draw_networkx_nodes(self.graph, pos,
                               nodelist=nodes,
                               node_color='r',
                               node_size=500,
                               alpha=0.5)

        nx.draw_networkx_nodes(self.graph, pos,
                               nodelist=[self.start],
                               node_color='b',
                               node_size=500,
                               alpha=1.0)

        nx.draw_networkx_nodes(self.graph, pos,
                               nodelist=[self.goal],
                               node_color='g',
                               node_size=500,
                               alpha=1.0)

        nx.draw_networkx_edges(self.graph, pos, width=1, alpha=0.5)

        labels = {}
        for i in range(0, self.num_nodes):
            labels[i] = str(i)

        nx.draw_networkx_labels(self.graph, pos, labels, font_size=16)
        plt.show()
        print("Rendering")

def create_new_qlearn_solver(model_size, qlearner):
    start = random.randint(0, model_size - 1)
    goal = start
    while goal == start:
        goal = random.randint(0, model_size - 1)

    qlearnsolver = QLearnSolver(model_size, start, goal, qlearner)
    qlearner.set_start_and_goal(start, goal)
    return qlearnsolver


def main():
    existing_file = ""

    if len(sys.argv) > 1:
        existing_file = sys.argv[1]

    num_execution_iterations = 1
    if existing_file == "":
        num_execution_iterations = 2000

    for exec_iter in range(0, num_execution_iterations):
        print("Execution Iteration: %s" % exec_iter)
        print("-" * 50)
        num_training_iterations = 10000
        model_size = 10
        qlearner = QLearner(model_size, 0.3)

        if existing_file == "":
            qlearnsolver = create_new_qlearn_solver(model_size, qlearner)
            with open('qlearnsolver.pkl', 'wb') as output:
                pickle.dump(qlearnsolver, output, pickle.HIGHEST_PROTOCOL)
        else:
            with open(existing_file, 'rb') as input:
                qlearnsolver = pickle.load(input)
                qlearnsolver.render()

        for i in range(0, num_training_iterations):
            qlearner.set_start_and_goal(qlearnsolver.start, qlearnsolver.goal)
            qlearnsolver.execute_training()

        print("Completed Training")
        path = qlearnsolver.execute()
        print("Start: %s End: %s" % (qlearnsolver.start, qlearnsolver.goal))
        print("Found path: %s" % path)
        if path[0] != qlearnsolver.start or path[-1] != qlearnsolver.goal or len(path) > 2:
            print("Error in predicting....")
            print("Q = ")
            for i in range(0, model_size):
                print(" ".join(str(j) for j in qlearner.Q[i]))
            qlearnsolver.render()
            path = qlearnsolver.execute(trace=True)

        if existing_file == "":
            os.remove("qlearnsolver.pkl")

        print("-" * 50)

if __name__ == "__main__":
    main()