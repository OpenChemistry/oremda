import base64
import io
import functools
from typing import Dict, Callable

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
        super().__init__(id, DisplayType.OneD)
        self.id = id
        self.notify = notify
        self.inputs: Dict[IdType, Port] = {}

    def add(self, sourceId: IdType, input: Port):
        if input.data is None:
            return

        x = list(input.data.data[0])
        y = list(input.data.data[1])

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
        super().__init__(id, DisplayType.OneD)
        self.id = id
        self.notify = notify

    def add(self, sourceId: IdType, input: Port):
        if input.data is None:
            return

        shape = input.data.data.shape
        scalars = input.data.data.flatten()

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
    img_src = base64.b64encode(file_obj.getvalue()).decode()
    file_obj.close()

    payload = {
        "displayId": self.id,
        "imageSrc": f"data:image/png;base64,{img_src}",
    }

    message = generic_message(ActionType.DisplayRender, payload)
    self.notify(message)


class RemoteRenderDisplayHandle1D(MatplotlibDisplayHandle1D):
    def __init__(self, id: IdType, notify: Callable[[NotificationMessage], None]):
        super().__init__(id)
        self.notify = notify
        self.render = functools.partial(remote_render, self)


class RemoteRenderDisplayHandle2D(MatplotlibDisplayHandle2D):
    def __init__(self, id: IdType, notify: Callable[[NotificationMessage], None]):
        super().__init__(id)
        self.notify = notify
        self.render = functools.partial(remote_render, self)
