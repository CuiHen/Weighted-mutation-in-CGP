# !/usr/bin/env python

"""

"""
import networkx.exception
import numpy as np


class NodeDependency:
    def __init__(self, params):
        self.params = params

        self.dependencies = {}
        # self.graph = nx.MultiDiGraph()
        self._init()

    def _init(self):
        """

        :return:
        """
        self.dependencies = {}
        for i in range(self.params["graph_width"] + self.params["nbr_inputs"] + self.params["nbr_outputs"]):
            self.dependencies[i] = []

    def add_dependency(self, node_id, prev_id):
        """
        Add the dependency from prev -> node
        :param node_id:
        :param prev_id:
        :return:
        """
        self.dependencies[node_id].append(prev_id)

    def remove_dependency(self, node_id, prev_id):
        """

        :param node_id:
        :param prev_id:
        :return:
        """
        self.dependencies[node_id].remove(prev_id)

    def contains_cycle(self, node_id, prev_id):
        """
        checks if there's a cycle when the connection prev -> node exists
        :param node_id:
        :param prev_id:
        :return:
        """
        to_check = []  # make empty list and extend the values to not directly pop the dependency values
        to_check.extend(self.dependencies[prev_id])
        while to_check:
            checking = to_check.pop()

            if checking == node_id:
                return True

            # append the new to check nodes
            to_check.extend(self.dependencies[checking])

        return False


if __name__ == '__main__':
    p = {}
    p["graph_width"] = 10
    p["nbr_inputs"] = 5
    p["nbr_outputs"] = 2
    n = NodeDependency(p)
    # (0, 1), (0, 2), (1, 4), (2, 5), (5, 4), (4, 6), (5, 6)
    n.add_dependency(2, 0)
    n.add_dependency(4, 2)
    n.add_dependency(4, 5)
    n.add_dependency(5, 2)
    n.add_dependency(6, 2)
    n.add_dependency(7, 4)
    n.add_dependency(8, 6)
    print(n.contains_cycle(7, 2))  # false
    print(n.contains_cycle(2, 7))  # true
    # cycle: 7 to 2; d.h. 2 hat connection0 to 7
