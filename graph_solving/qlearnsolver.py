import networkx as nx
import matplotlib.pyplot as plt
import random

class QLearnSolver:
    def __init__(self, num_nodes, start, goal):
        self.num_nodes = num_nodes
        self.start = start
        self.goal = goal
        self.graph = nx.DiGraph()

        assert 0 <= start <= num_nodes - 1
        assert 0 <= goal <= num_nodes - 1

        for i in range(0, num_nodes):
            self.graph.add_node(i)

        for i in range(0, num_nodes):
            n1 = random.randint(0, num_nodes - 1)
            n2 = random.randint(0, num_nodes - 1)
            if n1 == n2:
                continue
            self.graph.add_edge(n1, n2)

        # Make sure there is atleast one edge between the start and goal
        self.graph.add_edge(start, goal)

        # Add one more with a node in between
        b1 = random.randint(0, num_nodes - 1)
        self.graph.add_edge(start, b1)
        self.graph.add_edge(b1, goal)

        # Create reward matrix
        self.reward = [[0] * num_nodes for _ in range(0, num_nodes)]

        goal_reward = 100
        for u, v in self.graph.edges():
            if v == goal:
                self.reward[u][v] = goal_reward

    def get_reward_matrix(self):
        return self.reward

    def render(self):
        nodes = [i for i in range(0, self.num_nodes)]
        nodes.remove(self.start)
        nodes.remove(self.goal)

        pos = nx.spring_layout(self.graph)
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

def main():
    qlearnsolver = QLearnSolver(10, 3, 8)
    qlearnsolver.render()

if __name__ == "__main__":
    main()