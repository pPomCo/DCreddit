#!/bin/bash

# SBATCH options :
#SBATCH --job-name=JulianCorrelation
#SBATCH --output=bonsoir.txt

#SBATCH --mail-type=END
#SBATCH --mail-user=xzaitsevx@gmail.com

#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --partition=24CPUNodes


PROJECT_DIR=/projets/M2DC
TEAM_DIR=$PROJECT_DIR/team_JJJP

CONDA_ENV_DIR=$HOME/.conda/envs/DCreddit
GIT_DIR=$HOME/DCreddit

srun singularity exec /logiciels/containerCollections/CUDA10/vanilla_10.0.sif $CONDA_ENV_DIR/bin/python3 exploration.py

