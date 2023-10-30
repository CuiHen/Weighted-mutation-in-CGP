# Weighted-mutation-in-CGP

The code can be called in a command line.

For this, just call `cgp_main.py`. An example can be seen below:

`python cgp_main.py -d 1 -w 1 -maxw 500 -stepw 100 -n 100 -t DAG  `

It is possible to use the following command line arguments:
- `-d`: Choose Dataset:
  - `0`: Decode
  - `1`: Parity
  - `2`: Encode
  - `3`: Multiply
- `w`: If you want to use weights or not
  - `0`: No weights
  - `1`: Weights
- `maxw`: The highest value a weight can be
- `stepw`: The step size for weights
- `n`: Number of nodes for CGP
- `t`: CGP Type
  - `Normal`
  - `DAG`
- `average_inactivity`: True or False; If True, writes after training the number of iterations each node spend inactive


# Citation
This implementation was used for the following paper:

> Henning Cui, David Pätzel, Andreas Margraf and Jörg Hähner. 2023. Weighted mutation of connections to mitigate search space limitations in Cartesian Genetic Programming. In FOGA '23: Proceedings of the 17th ACM/SIGEVO Conference on Foundations of Genetic Algorithms, 30 August - 1 September 2023, Potsdam, Germany. Association for Computing Machinery, New York, NY, 50-60 DOI: 10.1145/3594805.3607130
