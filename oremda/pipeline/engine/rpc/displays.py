from oremda.display.matplotlib import (
    MatplotlibDisplayHandle1D,
    MatplotlibDisplayHandle2D,
)
from oremda.pipeline.messages import (
    ActionType,
    NotificationMessage,
    generic_message,
)
from oremda.typing import IdType
from typing import Callable
import base64
import io
import functools


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
