from typing import Dict, Callable

from oremda.display import DisplayHandle, DisplayType
from oremda.typing import IdType, Port

from ..messages import (
    ActionType,
    NotificationMessage,
    generic_message,
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
