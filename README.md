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
