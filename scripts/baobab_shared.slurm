#!/bin/bash
#SBATCH --mail-user=mads.sorensen@unige.ch
#SBATCH --job-name=DummyJobName
#SBATCH --output=DummyJobName.out
#SBATCH --error=DummyJobName.err
#SBATCH --partition=shared
#SBATCH --ntasks=1
#SBATCH --mem=8000
#SBATCH --time=12:00:00
#SBATCH --parsable

export PATH="/home/sorensen/anaconda/bin:$PATH"
export OMP_DYNAMIC=True
export OMP_NUM_THREADS=32

export MESASDK_ROOT=~/mesasdk
source $MESASDK_ROOT/bin/mesasdk_init.sh
export MESA_DIR=~/mesa-r8845

srun --cpu_bind=mask_cpu:0xffffffff ./python StartJobRLO.py
