import io
import functools
from typing import Dict, Callable, cast
import numpy as np

from oremda.display import DisplayHandle, DisplayType
from oremda.typing import IdType, Port

from ..messages import (
    ActionType,
    NotificationMessage,
    generic_message,
)
from oremda.display.matplotlib import (
    MatplotlibDisplayHandle1D,
    MatplotlibDisplayHandle2D,
)


class DisplayHandle1D(DisplayHandle):
    def __init__(self, id: IdType, notify: Callable[[NotificationMessage], None]):
        super(DisplayHandle, self).__init__(id, DisplayType.OneD)
        self.id = id
        self.notify = notify
        self.inputs: Dict[IdType, Port] = {}

    def add(self, sourceId: IdType, input: Port):
        if input.data is None:
            return

        data = cast(np.ndarray, input.data.data)

        x = list(data[0])
        y = list(data[1])

        label = None
        if input.meta is not None:
            label = input.meta.get("label")

        payload = {
            "displayId": self.id,
            "sourceId": sourceId,
            "x": x,
            "y": y,
            "label": label,
        }

        message = generic_message(ActionType.DisplayAddInput, payload)
        self.notify(message)

        self.render()

    def remove(self, sourceId: IdType):
        payload = {
            "displayId": self.id,
            "sourceId": sourceId,
        }

        message = generic_message(ActionType.DisplayRemoveInput, payload)
        self.notify(message)

        self.render()

    def clear(self):
        payload = {"displayId": self.id}

        message = generic_message(ActionType.DisplayClearInputs, payload)
        self.notify(message)

        self.render()

    def render(self):
        payload = {"displayId": self.id}

        message = generic_message(ActionType.DisplayRender, payload)
        self.notify(message)


class DisplayHandle2D(DisplayHandle):
    def __init__(self, id: IdType, notify: Callable[[NotificationMessage], None]):
        super(DisplayHandle, self).__init__(id, DisplayType.OneD)
        self.id = id
        self.notify = notify

    def add(self, sourceId: IdType, input: Port):
        if input.data is None:
            return

        data = cast(np.ndarray, input.data.data)
        shape = data.shape
        scalars = data.flatten()

        payload = {
            "displayId": self.id,
            "sourceId": sourceId,
            "scalars": scalars.tolist(),
            "shape": list(shape),
        }

        message = generic_message(ActionType.DisplayAddInput, payload)
        self.notify(message)

        self.render()

    def remove(self, sourceId: IdType):
        payload = {
            "displayId": self.id,
            "sourceId": sourceId,
        }

        message = generic_message(ActionType.DisplayRemoveInput, payload)
        self.notify(message)

        self.render()

    def clear(self):
        payload = {"displayId": self.id}

        message = generic_message(ActionType.DisplayClearInputs, payload)
        self.notify(message)

        self.render()

    def render(self):
        payload = {"displayId": self.id}

        message = generic_message(ActionType.DisplayRender, payload)
        self.notify(message)


def remote_render(self):
    file_obj = io.BytesIO()
    self.raw_render(file_obj)
    img_src = file_obj.getvalue()
    file_obj.close()

    payload = {
        "displayId": self.id,
        "imageSrc": img_src,
    }

    message = generic_message(ActionType.DisplayRender, payload)
    self.notify(message)


class RemoteRenderDisplayHandle1D(MatplotlibDisplayHandle1D):
    def __init__(self, id: IdType, notify: Callable[[NotificationMessage], None]):
        super(MatplotlibDisplayHandle1D, self).__init__(id)
        self.notify = notify
        self.render = functools.partial(remote_render, self)


class RemoteRenderDisplayHandle2D(MatplotlibDisplayHandle2D):
    def __init__(self, id: IdType, notify: Callable[[NotificationMessage], None]):
        super(MatplotlibDisplayHandle2D, self).__init__(id)
        self.notify = notify
        self.render = functools.partial(remote_render, self)
