#!/bin/bash
#SBATCH --account=ncemhub
#SBATCH --qos=debug
#SBATCH -C haswell
#SBATCH --time=00:01:00
#SBATCH -N 8

home=/global/homes/p/psavery/
venv_path=$home/virtualenvs
oremda_path=$venv_path/oremda

source $oremda_path/bin/activate
srun -n 8 python -u run.py
