# !/usr/bin/env python

import sys
import argparse
import numpy as np
import os

from overall_utils.runner_boolean import Runner
from overall_utils.params_boolean import params
from overall_utils.active_node_logger import CSVLogger

from datasets_boolean.boolean.bool_decode import BooleanBenchmarkDecode
from datasets_boolean.boolean.bool_encode import BooleanBenchmarkEncode
from datasets_boolean.boolean.multiply import Multiply
from datasets_boolean.boolean.parity import Parity

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dataset", type=int, help="Dataset nbr;\n0: Decode\n;1: Parity\n;2: Encode\n;3: Multiply",
                    choices=[0, 1, 2, 3])
parser.add_argument("-w", "--weighted", type=bool, help="Use weighted with True, non-weighted with False")
parser.add_argument("-maxw", "--max_weighted", type=int, help="")
parser.add_argument("-stepw", "--step_weighted", type=int, help="")
parser.add_argument("-n", "--nbr_nodes", type=int, help="Number of computational nodes")
parser.add_argument("-t", "--type", type=str, help="D", choices=["DAG", "Normal"])
parser.add_argument("--average_inactivity",
                    type=bool,
                    default=False,
                    help="True or False; If True, writes after training the number of iterations each node spend "
                         "inactive")

args = parser.parse_args()

params["max_iter_prob"] = args.max_weighted
params["weight_step"] = args.step_weighted

if args.type == "DAG":
    if args.weighted:
        if args.average_inactivity:
            from dag.utils.non_weighted.chromosomedag_test_freq import Chromosome
        else:
            from dag.utils.non_weighted.chromosomedag import Chromosome
    else:
        if args.average_inactivity:
            from dag.utils.weighted.chromosomedag_testfreq import Chromosome
        else:
            from dag.utils.weighted.chromosomedag import Chromosome
else:
    if args.weighted:
        if args.average_inactivity:
            from vanilla.utils.non_weighted.chromosome_freq import Chromosome
        else:
            from vanilla.utils.non_weighted.chromosome import Chromosome
    else:
        if args.average_inactivity:
            from vanilla.utils.weighted.chromosome_frequency import Chromosome
        else:
            from vanilla.utils.weighted.chromosome import Chromosome


def learn(path, parameters, data, label):
    # open a text file to log everything
    logger = CSVLogger(path, filename="output_file")
    logger.init_file()

    # init new Runner
    cgp_runner = Runner(parameters, data, label, Chromosome)

    # start the main training loop:
    for i in range(parameters["iterations"]):
        # start the evolution steps and the processes for evolution
        fitness, chromos = cgp_runner.evolve()

        if fitness <= 1e-6:
            break

    if args.average_inactivity:
        os.makedirs(os.path.join("outputs", "inactive_nodes"), exist_ok=True)
        temp_path = os.path.join("outputs",
                                 "inactive_nodes",
                                 f"{args.type}-{args.dataset}_maxw-{args.max_weighted}_stepw-{args.step_weighted}.txt")
        with open(temp_path, "w") as handle:
            for j, ch in enumerate(cgp_runner.chromosomes):
                ch.all_inactivitie_numbers.extend(list(np.where(ch.number_iterations_of_inactivity > 0)[0]))

                handle.write(f"{np.average(ch.all_inactivitie_numbers)}\n")
                np.savetxt(os.path.join("outputs",
                                        "inactive_nodes",
                                        f"chromosone_{j}_type_{args.type}_d"
                                        f"-{args.dataset}_maxw-"
                                        f"{args.max_weighted}_stepw-"
                                        f"{args.step_weighted}.txt"),
                           ch.all_inactivitie_numbers)

    logger.write_finished(i)
    # logger.write_active_nodes(chromos, i)
    logger.close()
    return


def main():
    dataset_nbr = args.dataset

    if dataset_nbr % 4 == 0:
        params["dataset"] = "decode"
        dataset = BooleanBenchmarkDecode()
    elif dataset_nbr % 4 == 1:
        params["dataset"] = "parity"
        dataset = Parity()
    elif dataset_nbr % 4 == 2:
        params["dataset"] = "encode"
        dataset = BooleanBenchmarkEncode()
    elif dataset_nbr % 4 == 3:
        params["dataset"] = "multiply"
        dataset = Multiply()
    else:
        raise NotImplementedError

    data, label = dataset()
    params["graph_width"] = args.nbr_nodes
    params["nbr_outputs"] = np.shape(label)[1]
    params["nbr_inputs"] = np.shape(data)[1]

    print("input variables: ", np.shape(data)[1])
    print("output variables: ", np.shape(label)[1])
    print(params)

    # non weighted
    if args.weighted == 0:
        path = os.path.join("outputs", args.type, "no_weights", params["dataset"])

    # weighted
    else:
        maxw = params["max_iter_prob"]
        stepw = params["weight_step"]
        path = os.path.join("outputs",
                            args.type,
                            f"maxw_{maxw}",
                            f"stepw_{stepw}",
                            params["dataset"])

    os.makedirs(path, exist_ok=True)

    learn(path=path,
          parameters=params,
          data=data,
          label=label)
    print("DONE")


if __name__ == '__main__':
    main()
