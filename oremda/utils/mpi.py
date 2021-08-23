try:
    from mpi4py import MPI
except ImportError:
    rank = 0
    world_size = 1
else:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    world_size = comm.Get_size()

mpi_rank = rank
mpi_world_size = world_size
