try:
    from mpi4py import MPI
except ImportError:
    rank = 0
else:
    rank = MPI.COMM_WORLD.Get_rank()

mpi_rank = rank
