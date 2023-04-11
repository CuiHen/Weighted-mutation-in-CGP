# !/usr/bin/env python

"""

"""
import random
import copy
import overall_utils.fitness_metrics as custom_loss


class Runner:
    def __init__(self, params, data, label, chromo):
        """

        :param params:
        :param data:
        :param label:
        :param chromo:
        """
        self.params = params
        self.data = data
        self.label = label

        # get the correct loss function
        self.fitness_func = custom_loss.fitness_boolean

        self.chromosomes = list()
        self.current_best_fitness_value_train = None
        self.current_fitness_values = []

        self.number_offsprings = params["nbr_offsprings"]

        for _ in range(self.number_offsprings):
            self.chromosomes.append(chromo(params))

        self.parent_id = random.randint(0, self.number_offsprings - 1)
        self.parent_chromosome = self.chromosomes[self.parent_id]

        # Stuff for probablistic mutation:
        # dict to check if the an active node was changed
        self.active_node_changed = {}
        for i in range(self.number_offsprings):
            self.active_node_changed[i] = True

    def get_parent(self):
        """
        Returns parent chromosome
        :return:
        """
        return self.parent_chromosome

    def get_current_fitness_value_train(self):
        """
        Returns the current best fitness value of all chromosomes
        :return:
        """
        return self.current_best_fitness_value_train

    def _calc_fitness(self, eval_mode=False):
        """
        Calculates the fitness given input and target
        :return:
        """
        fitness_dict = {}
        # iterate for every chromosome
        for i, chromosome in enumerate(self.chromosomes):
            # after the first iteration, this list should contain all fitness values of the previous iteration
            # as the parent has not changed, do not evaluate it again as the fitness value will stay the same
            if self.current_fitness_values and not eval_mode:
                if i == self.parent_id:
                    fitness_dict[i] = self.current_fitness_values[i]
                    continue

                # in case of for random mutation
                if not self.active_node_changed[i]:
                    fitness_dict[i] = self.current_fitness_values[i]
                    continue

            # else: new fitness values are calculated
            outputs = chromosome(self.data)
            loss_value = self.fitness_func(model_output=outputs, target=self.label)
            fitness_dict[i] = loss_value
            assert loss_value >= 0  # todo debug assert, remove later

        return fitness_dict


    def evolve(self):
        """
        Do one evolution step and set the new parent chromosome
        :return:
        """

        chromosome_fitness_values = self._calc_fitness()

        # neutral search
        # get all minimum value-keys
        min_fitness_value = min(chromosome_fitness_values.values())
        min_keys = [key for key, value in chromosome_fitness_values.items() if value == min_fitness_value]
        # and save the best fitness to avoid unnecessary evaluations later
        self.current_best_fitness_value_train = min_fitness_value
        self.current_fitness_values = list(chromosome_fitness_values.values())

        # if just one chromosome is the best: use this one
        if len(min_keys) == 1:
            self.parent_id = min_keys[0]
        else:
            # else: remove the previous parent key and get a new one
            if self.parent_id in min_keys:
                min_keys.remove(self.parent_id)
            self.parent_id = random.choice(min_keys)

        # set the new parent
        self.parent_chromosome = copy.deepcopy(self.chromosomes[self.parent_id])

        # evolve 4 new offsprings
        # the best parent stays the same
        for i in range(self.number_offsprings):
            self.chromosomes[i] = copy.deepcopy(self.parent_chromosome)

            # mutate
            if i != self.parent_id:
                self.chromosomes[i].mutate_single()
                self.active_node_changed[i] = True
            else:
                self.active_node_changed[i] = False

        return self.current_best_fitness_value_train, self.chromosomes

