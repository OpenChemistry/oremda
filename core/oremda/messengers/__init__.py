from .base import BaseMessenger
from .mqp import MQPMessenger

__all__ = [
    "BaseMessenger",
    "MQPMessenger",
    "MPIMessenger",
]

try:
    from .mpi import MPIMessenger
except ImportError:
    MPIMessenger = None


from oremda.plasma_client import PlasmaClient
from oremda.typing import LocationType


def Messenger(location: LocationType, plasma_client: PlasmaClient) -> BaseMessenger:
    messengers = {
        LocationType.Local: lambda: MQPMessenger(plasma_client),
        LocationType.Remote: lambda: MPIMessenger() if MPIMessenger else None,
    }

    if location == LocationType.Remote and MPIMessenger is None:
        raise Exception("Remote messenger is not available")

    return messengers[location]()
