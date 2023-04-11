# !/usr/bin/env python

"""
"""
import random

from overall_utils.function_list_boolean import Functions
from overall_utils.generate_random_nbrs import generate_random_number


class NodeDAG:
    def __init__(self, params, position, is_input_node=False, is_output_node=False):
        """

        :param params:
        :param position: The position in a node grid. the number of input nodes are included into this value
        :param is_input_node:
        :param is_output_node:
        """
        self.position = position
        self.is_input_node = is_input_node
        self.is_output_node = is_output_node
        self.params = params

        self.functions_list = Functions()

        self.function_id = -1
        self.connection0_id = -1
        self.connection1_id = -1

        self._get_random_function_id()
        self._get_random_connection_0_id()
        self._get_random_connection_1_id()

    def _get_random_function_id(self):
        """

        :return:
        """
        self.function_id = generate_random_number(0, len(self.functions_list) - 1, excluded=self.function_id)

    def _get_random_connection_0_id(self, dependencies=None):
        if self.is_input_node:
            # there are nbr_inputs many inputs with their nodes in [0, nbr_inputs]
            # self.connection0_id = None
            pass

        elif self.is_output_node:
            self.connection0_id = generate_random_number(0,
                                                         self.params["nbr_inputs"] + self.params["graph_width"] - 1,
                                                         self.connection0_id)

        else:
            # add input number and its position, -1 as it generates in range [0, x] instead of [0, x[
            if dependencies and not self.is_output_node:
                while True:
                    rand_conn = generate_random_number(0,
                                                       self.params["nbr_inputs"] + self.params["graph_width"] - 1,
                                                       self.connection0_id)
                    # no connection to self; get new value
                    if rand_conn == self.position:
                        continue

                    # if no cycle, its good. use it
                    if not dependencies.contains_cycle(self.position, rand_conn):
                        break

                dependencies.remove_dependency(self.position, self.connection0_id)
                self.connection0_id = rand_conn
                dependencies.add_dependency(self.position, self.connection0_id)

            else:
                # no dependency check necessary as no node is able to connect to an output node
                self.connection0_id = generate_random_number(0,
                                                             self.position - 1,
                                                             self.connection0_id)

    def _get_random_connection_1_id(self, dependencies=None):  #
        if self.is_input_node:
            # there are nbr_inputs many inputs with their nodes in [0, nbr_inputs]
            # self.connection1_id = None
            pass

        else:
            # add input number and its position, -1 as it generates in range [0, x] instead of [0, x[
            if dependencies and not self.is_output_node:
                while True:
                    rand_conn = generate_random_number(0,
                                                       self.params["nbr_inputs"] + self.params["graph_width"] - 1,
                                                       self.connection1_id)

                    if rand_conn == self.position:
                        continue

                    if not dependencies.contains_cycle(self.position, rand_conn):
                        break

                dependencies.remove_dependency(self.position, self.connection1_id)
                self.connection1_id = rand_conn
                dependencies.add_dependency(self.position, self.connection1_id)

            else:
                # no dependency check necessary as no node is able to connect to an output node
                self.connection1_id = generate_random_number(0,
                                                             self.position - 1,
                                                             self.connection1_id)

    def get_arity(self):
        return self.functions_list.nbr_params_dict[self.function_id]

    def calc_output(self, connection0_value, connection1_value):
        function = self.functions_list.function_dict[self.function_id]
        res = function(connection0_value,
                       connection1_value)
        return res

    def mutate(self, dependencies):
        if self.is_output_node:
            param = random.randint(0, 1)
        else:
            param = random.randint(0, 2)

        if param == 0:
            self._get_random_function_id()
        elif param == 1:
            self._get_random_connection_0_id(dependencies)
        elif param == 2:
            self._get_random_connection_1_id(dependencies)
