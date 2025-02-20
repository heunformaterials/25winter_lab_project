#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=20
#SBATCH --partition=g2
##
#SBATCH --job-name="FCC_Cu_slab_test"
#SBATCH --time=7-12:30
#Runtime limit: Day-HH:MM
#SBATCH -o STDOUT.%N.%j.out         # STDOUT, %N : nodename, %j : JobID
#SBATCH -e STDERR.%N.%j.err         # STDERR, %N : nodename, %j : JobID
#SBATCH --account=users

## HPC ENVIRONMENT DON'T REMOVE THIS PART
. /etc/profile.d/TMI.sh
##

mpiexec.hydra -genv I_MPI_DEBUG 5 -np $SLURM_NTASKS  /TGM/Apps/VASP/VASP_BIN/6.3.2/vasp.6.3.2.vtst.std.x
