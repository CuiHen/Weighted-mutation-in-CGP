# !/usr/bin/env python

"""

"""
import os
import csv
import ast

import gzip
import numpy as np


class CSVLogger:
    def __init__(self, file_path=None, filename=None):
        self.filename = os.path.join(file_path, filename)

        self.handle_active_nodes = None

    def init_file(self):
        os.makedirs(os.path.split(self.filename)[0], exist_ok=True)

        # if exists: replace with empty
        with open(self.filename + "_fitness.csv", "wt", newline='') as handle:
            pass
        with open(self.filename + "_active_nodes.txt", "w") as handle:
            pass

        # self.handle_active_nodes = gzip.open(self.filename + "_active_nodes.gz", "a")
        self.handle_active_nodes = open(self.filename + "_active_nodes.txt", "a")
        # self.writer_active_nodes =

        self.handle_fitness = open(self.filename + "_fitness.csv", "a", newline="")
        self.writer_fitness = csv.writer(self.handle_fitness, delimiter=";")

    def write_active_nodes(self, chromosomes, iteration):
        # Write the parameters into the csv file
        row = ""
        # row += f"{iteration};"
        for ch in chromosomes:
            # row += f"{ch.active_nodes_id};"
            row += f"{ch.nvr_active};"
        row += "\n"
        self.handle_active_nodes.write(row)

    def write_fitness(self, fitness, iteration):
        self.writer_fitness.writerow([f"{iteration}", f"{fitness}"])

    def write_finished(self, iteration):
        self.writer_fitness.writerow([f"Finished at: {iteration}"])

    def close(self):
        try:
            self.handle_active_nodes.close()
        except:
            pass
        try:
            self.handle_fitness.close()
        except:
            pass

    def read_active_nodes(self, filename):
        active_nodes = {0: [], 1: [], 2: [], 3: [], 4: []}

        with gzip.open(filename, "rb") as handle:
            # lines = csv.reader(handle, delimiter=";")
            lines = handle.read().decode("ascii")
            lines = lines.split("\n")
            # last element is empty
            lines = lines[:-1]

            lines = [l.split(";") for l in lines]
            # iterate through every entry
            for l in lines:
                # iterate through the nodes. Ignore first as this is only the iteration number
                for i in range(0, 5):
                    active_node_list = ast.literal_eval(l[i])
                    active_nodes[i].append(active_node_list)

        return active_nodes

    def read_convergence_speed(self, filename):
        with open(filename, "r") as handle:
            lines = handle.readlines()

        finished = lines[-1]
        finished = int(finished.replace("Finished at: ", "").replace("\n", ""))
        return finished


