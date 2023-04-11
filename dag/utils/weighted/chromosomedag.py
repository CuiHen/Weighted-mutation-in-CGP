# !/usr/bin/env python

import random
import numpy as np
import networkx as nx
from dag.utils.weighted.nodedag import NodeDAG
from dag.utils.node_dependency import NodeDependency


class Chromosome:
    def __init__(self, params):
        self.params = params

        # nodes_grid contains multiple nodes-lists. each list in nodes_grid is one column
        self.nodes_grid = list()

        # the active nodes id set contains all active nodes. However, the input nodes are not in this set
        self.active_nodes_id = set()
        self.mutations_counter = 0
        # self.threshold = random.uniform(-10, 10)
        self.output_node_ids = [i for i in range(self.params["graph_width"] + self.params["nbr_inputs"],
                                                 self.params["graph_width"] + self.params["nbr_inputs"] +
                                                 self.params["nbr_outputs"])]

        # create dictionary which describes how many iterations ago a node was active. ignore output nodes as they
        # must always be active
        # self.last_active = {i: params["max_iter_prob"] for i in
        #                     range(self.params["graph_width"] + self.params["nbr_inputs"])}

        self.last_active = np.zeros(shape=(self.params["graph_width"] + self.params["nbr_inputs"],), dtype=np.int32) \
                           + params["max_iter_prob"]

        self.nvr_active = np.zeros(shape=(self.params["graph_width"] + self.params["nbr_inputs"],), dtype=np.bool8)

        # helper list so it must not be created each time
        self.helper_all_nodes = set(np.arange(self.params["nbr_inputs"] + self.params["graph_width"]))
        self.helper_output_nodes = set(np.arange(self.params["nbr_inputs"] + self.params["graph_width"],
                                                 self.params["graph_width"] + self.params["nbr_inputs"] +
                                                 self.params["nbr_outputs"]))

        self.dependencies = NodeDependency(params)
        # self._digraph = nx.MultiDiGraph()
        self._digraph = nx.DiGraph()

        self._init_graph()
        self._set_dependency()

    def _init_graph(self):
        """

        :return:
        """
        # fill the graph with input nodes first.
        for i in range(0,
                       self.params["nbr_inputs"]):
            node = NodeDAG(params=self.params,
                           position=i,
                           is_input_node=True)
            # node._get_random_connection_0_id(dependencies=self.dependencies)
            # node._get_random_connection_1_id(dependencies=self.dependencies)
            self.nodes_grid.append(node)
            # self.nodes_grid.append(NodeDAG(params=self.params,
            #                                position=i,
            #                                is_input_node=True))

        # now fill the graph with the inner nodes
        for i in range(self.params["nbr_inputs"],
                       self.params["nbr_inputs"] + self.params["graph_width"]):
            node = NodeDAG(params=self.params,
                           position=i)
            # node._get_random_connection_0_id(dependencies=self.dependencies)
            # node._get_random_connection_1_id(dependencies=self.dependencies)
            self.nodes_grid.append(node)
            #self.nodes_grid.append(NodeDAG(params=self.params,
            #                                position=i))

        # at last, output nodes
        for i in range(self.params["nbr_inputs"] + self.params["graph_width"],
                       self.params["nbr_inputs"] + self.params["graph_width"] + self.params["nbr_outputs"]):
            # self.nodes_grid.append(NodeDAG(params=self.params,
            #                                position=i,
            #                                is_output_node=True))
            node = NodeDAG(params=self.params,
                           position=i,
                           is_output_node=True)
            # node._get_random_connection_0_id(dependencies=self.dependencies)
            # node._get_random_connection_1_id(dependencies=self.dependencies)
            self.nodes_grid.append(node)

        self._get_active_nodes()

    def _set_dependency(self):
        for node_id in range(self.params["nbr_inputs"], self.params["nbr_inputs"] + self.params["graph_width"]):
            current_node = self.nodes_grid[node_id]

            connection0_id = current_node.connection0_id
            self.dependencies.add_dependency(node_id, connection0_id)

            connection1_id = current_node.connection1_id
            self.dependencies.add_dependency(node_id, connection1_id)

    def _pop_dict_key(self, dictionary: dict):
        """
        Pops the last key and returns it
        :return:
        """
        popped_key = list(dictionary.keys()).pop()
        dictionary.pop(popped_key)

        return popped_key

    def _update_last_active_dictionary(self):
        """
        Update the last-active dictionary
        :return:
        """
        # get relative difference to get the inactive nodes
        inactive_nodes = self.helper_all_nodes.difference(self.active_nodes_id)
        # get all active nodes but without the output nodes
        active_nodes_without_output = set(self.active_nodes_id).difference(self.helper_output_nodes)

        for node_id in inactive_nodes:
            self.last_active[node_id] = min(self.last_active[node_id] + self.params["weight_step"],
                                            self.params["max_iter_prob"])

        for node_id in active_nodes_without_output:
            self.last_active[node_id] = self.params["min_iter_prob"]

        self.nvr_active[list(active_nodes_without_output)] = True

    def _get_active_nodes(self):
        """
        Get all active nodes
        :return:
        """

        # at first, reset the dependencies to fill them later on
        self._digraph.clear()

        # at first, create a directed, acyclic graph with networkx
        # to do this, get the edge-vertice connection first
        # helper-set. while this set is not empty, there are still nodes to check.
        nodes_id_to_check = {}
        # second helper set to check if a node is already visited
        visited = {}
        for output_node in reversed(self.output_node_ids):
            nodes_id_to_check[output_node] = None
            visited[output_node] = None

        # connections = []
        while nodes_id_to_check:
            current_node_id = self._pop_dict_key(nodes_id_to_check)
            current_node = self.nodes_grid[current_node_id]

            # case: input node. does not have predecessor
            if current_node.is_input_node:
                continue

            # get the connection to the previous node
            connection_0 = current_node.connection0_id
            # if its already visited, ignore it. Else, look it up
            if connection_0 not in visited:
                nodes_id_to_check[connection_0] = None
                visited[connection_0] = None
            self._digraph.add_edge(connection_0, current_node_id)
            # connections.append((connection_0, current_node_id))

            # if output node: the second connection is not used
            if current_node.is_output_node:
                continue

            nbr_params = current_node.get_arity()
            # in case the second connection1 is used, nbr_params == 2. Then, connection1 must be considered too
            if nbr_params == 2:
                connection_1 = current_node.connection1_id

                if connection_1 not in visited:
                    nodes_id_to_check[connection_1] = None
                    visited[connection_1] = None
                # connections.append((connection_1, current_node_id))
                self._digraph.add_edge(connection_1, current_node_id)

        # self._digraph.add_edges_from(connections)
        # get a topological sort
        self.active_nodes_id = list(nx.topological_sort(self._digraph))

    def __call__(self, inputs):
        # set an output grid
        # the node outputs will be saved here and used by later nodes
        outputs = {}

        # travers all active nodes, from input to output node
        for current_node_id in self.active_nodes_id:
            current_width = current_node_id
            current_node = self.nodes_grid[current_width]

            # case input/output node
            if current_node.is_input_node:
                # if input node: the position n is also the pointer to the n-th input attribute
                input_pointer = current_node.position
                outputs[current_node_id] = inputs[:, input_pointer]
            # case output node. If a node is referencing an output node, treat it as an identity function
            elif current_node.is_output_node:
                outputs[current_node_id] = outputs[current_node.connection0_id]

            else:
                # case: a normal node.
                # calculate the output of the node
                if current_node.get_arity() == 1:
                    # arity == 1:
                    connection0 = current_node.connection0_id
                    outputs[current_node_id] = current_node.calc_output(outputs[connection0], None)
                else:
                    # arity == 2
                    connection0 = current_node.connection0_id
                    connection1 = current_node.connection1_id

                    outputs[current_node_id] = current_node.calc_output(outputs[connection0], outputs[connection1])

        outs = list()
        for output_nodes in self.output_node_ids:
            outs.append(outputs[output_nodes])
        outs = np.array(outs).T

        return outs

    def mutate_single(self):
        self._update_last_active_dictionary()

        # mutate variables
        while True:
            # get random node id's to mutate
            node_id = random.randint(self.params["nbr_inputs"],
                                     self.params["nbr_inputs"] + self.params["graph_width"] + self.params[
                                         "nbr_outputs"] - 1)

            # self.nodes_grid[node_id].mutate(self.dependencies, list(self.last_active.values()))
            self.nodes_grid[node_id].mutate(self.dependencies, self.last_active)

            if node_id in self.active_nodes_id:
                self._get_active_nodes()
                break


if __name__ == '__main__':
    import utils.params as param

    ch = ChromosomeDAG(params=param.params)
    print(ch(np.array([[1., 1., 1., 1., 1.], [2., 2., 2., 2., 2.], [3., 3., 3., 3., 3.]])))
