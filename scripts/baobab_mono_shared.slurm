#!/bin/bash
#SBATCH --mail-user=mads.sorensen@unige.ch
#SBATCH --job-name=DummyJobName
#SBATCH --output=DummyJobName.out
#SBATCH --error=DummyJobName.err
#SBATCH --partition=mono-shared
#SBATCH --cpus-per-task=8
#SBATCH --mem=8000
#SBATCH --time=3:00:00
#SBATCH --parsable

export PATH="/home/sorensen/anaconda/bin:$PATH"

export MESASDK_ROOT=~/mesasdk
source $MESASDK_ROOT/bin/mesasdk_init.sh
export MESA_DIR=~/mesa-r8845

srun python StartJobRLO.py
