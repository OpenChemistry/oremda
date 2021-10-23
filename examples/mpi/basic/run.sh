#!/bin/bash
#SBATCH --account=ncemhub
#SBATCH --qos=debug
#SBATCH -C haswell
#SBATCH --time=00:10:00
#SBATCH -N 8

home=/global/homes/p/psavery/
venv_path=$home/virtualenvs
oremda_path=$venv_path/oremda

export MPICH_MAX_THREAD_SAFETY=multiple
export PYTHONUNBUFFERED=1

export OREMDA_DATA_DIR=$SCRATCH/data/oremda
export OREMDA_CONTAINER_TYPE=singularity
export OREMDA_SIF_DIR=images
export OREMDA_OPERATOR_CONFIG_FILE="operator_config.json"

source $oremda_path/bin/activate
srun -n 8 oremda run pipeline.json
