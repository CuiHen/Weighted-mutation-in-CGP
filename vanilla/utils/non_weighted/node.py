# !/usr/bin/env python

"""
"""
import random

from overall_utils.function_list_boolean import Functions
from overall_utils.generate_random_nbrs import generate_random_number


class Node:
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

        # self.param0_range = self.params["parameter_0_range"]

        self.functions_list = Functions()

        self.function_id = -1
        self.connection0_id = None
        self.connection1_id = None
        # self.parameter0 = -1

        self._get_random_function_id()
        # self._get_random_param_0()

        if not is_input_node:
            self._get_random_connection_0_id()
            self._get_random_connection_1_id()

    def _get_random_function_id(self):
        """

        :return:
        """
        self.function_id = generate_random_number(0, len(self.functions_list) - 1, excluded=self.function_id)

    def _get_random_connection_0_id(self):
        if self.is_input_node:
            # there are nbr_inputs many inputs with their nodes in [0, nbr_inputs]
            self.connection0_id = None

        elif self.is_output_node:
            self.connection0_id = generate_random_number(0,
                                                         self.params["nbr_inputs"] + self.params["graph_width"] - 1,
                                                         self.connection0_id)

        else:
            # add input number and its position, -1 as it generates in range [0, x] instead of [0, x[
            self.connection0_id = generate_random_number(0,
                                                         self.position - 1,
                                                         self.connection0_id)

    def _get_random_connection_1_id(self):  #
        if self.is_input_node:
            # there are nbr_inputs many inputs with their nodes in [0, nbr_inputs]
            self.connection1_id = None

        elif self.is_output_node:
            self.connection1_id = generate_random_number(0,
                                                         self.params["nbr_inputs"] + self.params["graph_width"] - 1,
                                                         self.connection1_id)

        else:
            # add input number and its position, -1 as it generates in range [0, x] instead of [0, x[
            self.connection1_id = generate_random_number(0,
                                                         self.position - 1,
                                                         self.connection1_id)

    # def _get_random_param_0(self):
    #     self.parameter0 = random.uniform(self.param0_range[0], self.param0_range[1])

    def get_nbr_function_params(self):
        return self.functions_list.nbr_params_dict[self.function_id]

    def calc_output(self, connection0_value, connection1_value):
        function = self.functions_list.function_dict[self.function_id]
        # res = function(connection0_value,
        #                connection1_value,
        #                self.parameter0)
        res = function(connection0_value,
                       connection1_value)
        return res

    def mutate(self):
        if self.is_output_node:
            param = random.randint(0, 1)
        else:
            param = random.randint(0, 2)

        if param == 0:
            self._get_random_function_id()
        elif param == 1:
            self._get_random_connection_0_id()
        elif param == 2:
            self._get_random_connection_1_id()
        # elif param == 3:
        #     # Veränderung param0
        #     # Entweder ganz neu, oder um max +-10% verändern
        #     if bool(random.getrandbits(1)):
        #         self._get_random_param_0()
        #     else:
        #         # erstelle eine zahl zwischen -0.1 und +0.1, um jeweils max 10 prozent dazu addieren oder subtrahieren
        #         # zu können
        #         percent = random.uniform(-.1, .1)
        #         self.parameter0 = self.parameter0 * percent + self.parameter0
