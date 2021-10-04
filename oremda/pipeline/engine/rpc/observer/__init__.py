from typing import Callable, Dict

from oremda.typing import PortKey, Port
from oremda.pipeline import Pipeline, OperatorNode, PipelineObserver
from oremda.pipeline.operator import OperatorException

from ..messages import (
    pipeline_started,
    pipeline_completed,
    operator_started,
    operator_completed,
    operator_error,
    NotificationMessage,
)


class ServerPipelineObserver(PipelineObserver):
    def __init__(self, notify: Callable[[NotificationMessage], None]):
        self.notify = notify

    def on_start(self, pipeline: Pipeline):
        message = pipeline_started({"id": pipeline.id})
        self.notify(message)

    def on_complete(self, pipeline: Pipeline):
        message = pipeline_completed({"id": pipeline.id})
        self.notify(message)

    def on_operator_start(
        self, pipeline: Pipeline, operator: OperatorNode, inputs: Dict[PortKey, Port]
    ):
        message = operator_started(
            {"pipelineId": pipeline.id, "operatorId": operator.id}
        )
        self.notify(message)

    def on_operator_complete(
        self, pipeline: Pipeline, operator: OperatorNode, outputs: Dict[PortKey, Port]
    ):
        message = operator_completed(
            {"pipelineId": pipeline.id, "operatorId": operator.id}
        )
        self.notify(message)

    def on_operator_error(
        self, pipeline: Pipeline, operator: OperatorNode, error: OperatorException
    ):
        message = operator_error(
            {
                "pipelineId": pipeline.id,
                "operatorId": operator.id,
                "errorString": error.error_string,
            }
        )
        self.notify(message)
