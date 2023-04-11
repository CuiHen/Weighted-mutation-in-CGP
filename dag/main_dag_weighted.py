# !/usr/bin/env python

"""
imports are not pretty

"""
from tqdm import tqdm

import sys
import argparse
import numpy as np
import os

from overall_utils.runner_boolean import Runner
from overall_utils.params_boolean import params
from overall_utils.active_node_logger import CSVLogger
from overall_utils.check_doen import check_done

from datasets_boolean.boolean.bool_decode import BooleanBenchmarkDecode
from datasets_boolean.boolean.bool_encode import BooleanBenchmarkEncode
from datasets_boolean.boolean.multiply import Multiply
from datasets_boolean.boolean.parity import Parity

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--slurm_nbr", type=int, help="Slurm number")
parser.add_argument("-d", "--dataset", type=int, help="Dataset nbr")
parser.add_argument("-w", "--weighted", type=int, help="Use weighted with 1, non-weighted with 0")
parser.add_argument("-maxw", "--max_weighted", type=int, help="")
parser.add_argument("-stepw", "--step_weighted", type=int, help="")

args = parser.parse_args()

params["max_iter_prob"] = args.max_weighted
params["weight_step"] = args.step_weighted

if args.weighted == 0:
    # from dag.utils.non_weighted.chromosomedag_test_freq import ChromosomeDAG
    from dag.utils.non_weighted.chromosomedag import Chromosome
elif args.weighted == 1:
    # from dag.utils.weighted.chromosomedag_testfreq import ChromosomeDAG
    from dag.utils.weighted.chromosomedag import ChromosomeDAG

from time import time


def learn(path, parameters, data, label):
    # open a text file to log everything
    logger = CSVLogger(path)
    logger.init_file()

    # init new islands
    cgp_runner = Runner(parameters, data, label, Chromosome)

    # start the main training loop:
    for i in range(parameters["iterations"]):
        # start the evolution steps and the processes for evolution
        fitness, chromos = cgp_runner.evolve()

        if fitness <= 1e-6:
            break

        # print me something spicy
        # if i % 50 == 0:
        #     # get best fitness
        #     fitness_train = cgp_runner.get_current_fitness_value_train()
        #
        #     logger.write_fitness(fitness_train, i)
        # #     handle.write("TRAIN: Iteration: {}, min mcc value: {}\n".format(i, fitness_train))

        # evaluation step with the best chromosome

    # for ch in cgp_runner.chromosomes:
    #     print(np.average(ch.all_inactivitie_numbers))

    # os.makedirs("dag_TEMP_FREQUENCY_INACTIVITY_ANALYSIS", exist_ok=True)
    # with open(os.path.join("dag_TEMP_FREQUENCY_INACTIVITY_ANALYSIS", f"{args.slurm_nbr}_d-{args.dataset}_maxw-"
    #                                                              f"{args.max_weighted}_stepw-"
    #                                                              f"{args.step_weighted}.txt"), "w") as handle:
    #     for i, ch in enumerate(cgp_runner.chromosomes):
    #         ch.all_inactivitie_numbers.extend(list(np.where(ch.number_iterations_of_inactivity > 0)[0]))
    #
    #         handle.write(f"{np.average(ch.all_inactivitie_numbers)}\n")
    #         np.savetxt(os.path.join("dag_TEMP_FREQUENCY_INACTIVITY_ANALYSIS", f"nr_{i}_np_{args.slurm_nbr}_d"
    #                                                                       f"-{args.dataset}_maxw-"
    #                                                                       f"{args.max_weighted}_stepw-"
    #                                                                       f"{args.step_weighted}.txt"),
    #                    ch.all_inactivitie_numbers)
    # print()
    logger.write_finished(i)
    # logger.write_active_nodes(chromos, i)
    logger.close()
    return


def main():
    # import random
    # np.random.seed(0)
    # raise AssertionError("RANDOM SEED 0")
    # random.seed(0)


    params["number_goldmann_mutation"] = 1

    slurm_nbr = args.dataset

    # classification
    # single, dag
    if slurm_nbr % 4 == 0:

        params["dataset"] = "decode"
        dataset = BooleanBenchmarkDecode()
        data, label = dataset()
        # params["graph_width"] = 500
        params["graph_width"] = 100
        params["nbr_outputs"] = np.shape(label)[1]
    elif slurm_nbr % 4 == 1:
        params["dataset"] = "parity"
        dataset = Parity()
        data, label = dataset()
        params["graph_width"] = 100
        params["nbr_outputs"] = np.shape(label)[1]
    elif slurm_nbr % 4 == 2:
        params["dataset"] = "encode"
        dataset = BooleanBenchmarkEncode()
        data, label = dataset()
        params["graph_width"] = 100
        params["nbr_outputs"] = np.shape(label)[1]
    elif slurm_nbr % 4 == 3:
        params["dataset"] = "multiply"
        dataset = Multiply()
        data, label = dataset()
        params["graph_width"] = 100
        # params["graph_width"] = 2000
        params["nbr_outputs"] = np.shape(label)[1]
    else:
        raise NotImplementedError("Dataset , etc. slurm nbr. {}".format(slurm_nbr))

    print("input variables: ", np.shape(data)[1])
    print("output variables: ", np.shape(label)[1])
    print(params)

    if args.weighted == 0:
        path = "./Test_dag_non_weighted/{}/{}".format(params["dataset"], args.slurm_nbr)

    elif args.weighted == 1:
        dset = params["dataset"]
        maxw = params["max_iter_prob"]
        stepw = params["weight_step"]
        path = f"./PYTHONOUT/Test_dag_weighted_maxw_{maxw}_stepw_{stepw}/{dset}/{args.slurm_nbr}"
        # path = f"./EVALUATION/Test_dag_weighted_maxw_{maxw}_stepw_{stepw}/{dset}/{args.slurm_nbr}"

    os.makedirs(os.path.split(path)[0], exist_ok=True)

    params["nbr_inputs"] = np.shape(data)[1]

    # check_done(path)

    start = time()

    learn(path=path,
          parameters=params,
          data=data,
          label=label)
    print("DONE")
    print(time() - start)


if __name__ == '__main__':
    main()
