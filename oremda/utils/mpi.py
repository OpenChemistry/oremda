try:
    from mpi4py import MPI
except ImportError:
    import socket

    rank = 0
    world_size = 1
    host_name = socket.gethostname()
else:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    world_size = comm.Get_size()
    host_name = MPI.Get_processor_name()

mpi_rank = rank
mpi_world_size = world_size
mpi_host_name = host_name
