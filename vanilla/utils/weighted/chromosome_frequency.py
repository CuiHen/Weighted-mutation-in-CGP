# !/usr/bin/env python

"""
schaue, ob ein aktiver knoten verändert wurde. Wenn nein, dann return den selben fitness value
"""
import random
import numpy as np
from vanilla.utils.weighted.node import Node


class Chromosome:
    def __init__(self, params):
        self.params = params
        self.output_type = params["output_type"]

        # nodes_grid contains multiple nodes-lists. each list in nodes_grid is one column
        self.nodes_grid = list()
        # the active nodes id set contains all active nodes. However, the input nodes are not in this set
        self.active_nodes_id = set()
        self.mutations_counter = 0
        # self.threshold = random.uniform(-10, 10)
        self.output_node_ids = [i for i in range(self.params["graph_width"] + self.params["nbr_inputs"],
                                                 self.params["graph_width"] + self.params["nbr_inputs"] +
                                                 self.params["nbr_outputs"])]

        # create dictionary which describes how many iterations ago a node was active. do not ignore output nodes to not
        # trigger errors later down the line
        # self.last_active = {i: params["max_iter_prob"] for i in
        #                     range(self.params["graph_width"] + self.params["nbr_inputs"] + self.params[
        #                     "nbr_outputs"])}
        self.last_active = np.zeros(shape=(self.params["graph_width"] + self.params["nbr_inputs"],), dtype=np.int32) \
                           + params["max_iter_prob"]

        self.nvr_active = np.zeros(shape=(self.params["graph_width"] + self.params["nbr_inputs"],), dtype=np.bool8)

        # helper list so it must not be created each time
        self.helper_all_nodes = set(np.arange(self.params["nbr_inputs"] + self.params["graph_width"]))
        self.helper_output_nodes = set(np.arange(self.params["nbr_inputs"] + self.params["graph_width"],
                                                 self.params["graph_width"] + self.params["nbr_inputs"] +
                                                 self.params["nbr_outputs"]))

        self.number_iterations_of_inactivity = np.array(
            [0 for _ in range(self.params["nbr_inputs"] + self.params["graph_width"])])
        self.all_inactivitie_numbers = []

        self._init_graph()

    def _init_graph(self):
        # fill the graph with input nodes first.
        for i in range(self.params["nbr_inputs"]):
            self.nodes_grid.append(Node(params=self.params,
                                        position=i,
                                        is_input_node=True))

        # now fill the graph with the inner nodes
        for i in range(self.params["nbr_inputs"], self.params["nbr_inputs"] + self.params["graph_width"]):
            self.nodes_grid.append(Node(params=self.params,
                                        position=i))

        # at last, output nodes
        for i in range(self.params["nbr_inputs"] + self.params["graph_width"],
                       self.params["nbr_inputs"] + self.params["graph_width"] + self.params["nbr_outputs"]):
            self.nodes_grid.append(Node(params=self.params,
                                        position=i,
                                        is_output_node=True))

        self._get_active_nodes()

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
            self.number_iterations_of_inactivity[node_id] += 1

        for node_id in active_nodes_without_output:
            self.last_active[node_id] = self.params["min_iter_prob"]

            if self.number_iterations_of_inactivity[node_id] > 0:
                self.all_inactivitie_numbers.append(self.number_iterations_of_inactivity[node_id])
                self.number_iterations_of_inactivity[node_id] = 0

        self.nvr_active[list(active_nodes_without_output)] = True

    def _get_active_nodes(self):
        """
        Check, which node is active. Begin at output node and iterate from the back to the beginning
        :return:
        """
        # empty the active_nodes_id set and insert the output nodes
        self.active_nodes_id = set()
        for output_node in self.output_node_ids:
            self.active_nodes_id.add(output_node)

        # helper-set. while this set is not empty, there are still nodes to check.
        nodes_id_to_check = set()
        for output_node in self.output_node_ids:
            nodes_id_to_check.add(output_node)

        # start the search for every active node
        while nodes_id_to_check:
            # work from output node to input node. get the current node here
            width_nr = nodes_id_to_check.pop()

            current_node = self.nodes_grid[width_nr]

            if current_node.is_input_node:
                # case: input node. does not have predecessor
                continue

            # get the connection to the previous node and add it to the lists
            connection_0 = current_node.connection0_id

            if connection_0 not in self.active_nodes_id:  # a new node
                nodes_id_to_check.add(connection_0)
                self.active_nodes_id.add(connection_0)

            nbr_params = current_node.get_nbr_function_params()
            # in case the second connection1 is used, nbr_params == 2. Then, connection1 must be considered too
            if nbr_params == 2:
                connection_1 = current_node.connection1_id

                if connection_1 not in self.active_nodes_id:  # new node
                    nodes_id_to_check.add(connection_1)
                    self.active_nodes_id.add(connection_1)

        # sort it for the call
        self.active_nodes_id = sorted(self.active_nodes_id)

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
                if current_node.get_nbr_function_params() == 1:
                    # arity == 1:
                    connection0 = current_node.connection0_id
                    outputs[current_node_id] = current_node.calc_output(outputs[connection0], None)
                else:
                    # arity == 2
                    connection0 = current_node.connection0_id
                    connection1 = current_node.connection1_id
                    outputs[current_node_id] = current_node.calc_output(outputs[connection0], outputs[connection1])

        if self.output_type == "binary":
            # last current_node_id should always be the output node
            out = np.where(outputs[current_node_id] < 0, 1, 0)

        elif self.output_type == "scalar":
            # last current_node_id should always be the output node
            out = outputs[current_node_id]

        elif self.output_type == "categorical":  # categorical
            outs = list()
            for output_nodes in self.output_node_ids:
                outs.append(outputs[output_nodes])
            out = np.argmax(outs, axis=0)

        elif self.output_type == "boolean":
            outs = list()
            for output_nodes in self.output_node_ids:
                outs.append(outputs[output_nodes])
            out = np.array(outs).T

        else:
            raise UserWarning("Output type not defined")

        return out

    def mutate_single(self):
        self._update_last_active_dictionary()
        # mutate variables
        while True:
            # get random node id's to mutate
            node_id = random.randint(self.params["nbr_inputs"],
                                     self.params["nbr_inputs"] + self.params["graph_width"] + self.params[
                                         "nbr_outputs"] - 1)

            # self.nodes_grid[node_id].mutate(list(self.last_active.values())[:node_id])
            self.nodes_grid[node_id].mutate(self.last_active[:node_id])

            if node_id in self.active_nodes_id:
                self._get_active_nodes()
                break

    def mutate_goldman_multi(self, nbr_active_mutations=1):
        # reset the counter
        raise NotImplementedError
        self.mutations_counter = 0

        # mutate variables
        while True:
            # get random node id's to mutate
            node_length_id = random.randint(0, self.params["graph_width"] - 1)

            self.nodes_grid[node_length_id].mutate()

            if node_length_id in self.active_nodes_id:
                self.mutations_counter += 1

                self._get_active_nodes()

                if self.mutations_counter >= nbr_active_mutations:
                    break

    def mutate_random(self, p):
        """
        Mutate every node with a probability p
        :param p:
        :return:
        """
        raise NotImplementedError

        # Flag for the runner. If this flag is False, no active node was mutated and there's no need
        # to evaluate the chromosome a second time
        active_node_mutated = False

        for i in range(self.params["graph_width"]):
            if random.random() <= p:
                self.nodes_grid[i].mutate()
                # check if an active node is hit
                if i in self.active_nodes_id:
                    active_node_mutated = True

        self._get_active_nodes()

        return active_node_mutated

    def mutate_complex_random(self, p_active, p_inactive):
        """

        :param p_active:
        :param p_inactive:
        :return:
        """
        raise NotImplementedError
        # Flag for the runner. If this flag is False, no active node was mutated and there's no need
        # to evaluate the chromosome a second time
        active_node_mutated = False

        for i in range(self.params["graph_width"]):
            # case: active node:
            if i in self.active_nodes_id:
                if random.random() <= p_active:
                    self.nodes_grid[i].mutate()
                    self._get_active_nodes()
                    active_node_mutated = True

            else:  # case: inactive
                if random.random() <= p_inactive:
                    self.nodes_grid[i].mutate()

        return active_node_mutated


if __name__ == '__main__':
    import cgp_classification.utils.params as param

    ch = Chromosome(params=param.params, output_type="binary")
    print(ch(np.array([[1., 1., 1., 1., 1.], [2., 2., 2., 2., 2.], [3., 3., 3., 3., 3.]])))
