from oremda.messengers import Messenger
from oremda.typing import (
    DisplayNodeJSON,
    DisplayType,
    EdgeJSON,
    DataType,
    IdType,
    JSONType,
    LocationType,
    NodeJSON,
    OperatorNodeJSON,
    PipelineJSON,
    Port,
    PortKey,
    PortInfo,
)
from typing import Any, Optional, Dict, Sequence, Set, Type, TypeVar, Generator, Tuple
from oremda.operator import OperatorHandle
from oremda.utils.id import unique_id, port_id
from oremda.typing import PortType, NodeType, IOType
from oremda.registry import Registry
from oremda.plasma_client import PlasmaClient
from oremda.display import DisplayFactory, DisplayHandle, NoopDisplayHandle


class PipelineEdge:
    def __init__(
        self,
        output_node_id: IdType,
        output_port: PortInfo,
        input_node_id: IdType,
        input_port: PortInfo,
        id: Optional[IdType] = None,
    ):
        self.id = unique_id(id)
        self.output_node_id = output_node_id
        self.input_node_id = input_node_id
        self.output_port = output_port
        self.input_port = input_port


class PipelineNode:
    def __init__(self, t: NodeType, id: Optional[IdType] = None):
        self._id = unique_id(id)
        self._type = t
        self._inputs: Dict[PortKey, PortInfo] = {}
        self._outputs: Dict[PortKey, PortInfo] = {}

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def inputs(self):
        return self._inputs

    @inputs.setter
    def inputs(self, inputs: Dict[PortKey, PortInfo]):
        self._inputs = inputs

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, outputs: Dict[PortKey, PortInfo]):
        self._outputs = outputs

    def has(self, port: PortInfo, io: IOType):
        _port = None

        if io == IOType.In:
            _port = self._inputs.get(port.name)
        else:
            _port = self._outputs.get(port.name)

        if _port is None:
            return False

        return _port == port


class OperatorNode(PipelineNode):
    def __init__(self, id=None):
        super().__init__(NodeType.Operator, id)
        self._operator: Optional[OperatorHandle] = None

    @property
    def operator(self):
        return self._operator

    @operator.setter
    def operator(self, operator: OperatorHandle):
        self._operator = operator


class DisplayNode(PipelineNode):
    def __init__(self, id=None, display_type: DisplayType = DisplayType.OneD):
        super().__init__(NodeType.Display, id)
        self._display_type = display_type
        self._display: Optional[DisplayHandle] = None
        self._inputs = {"in": PortInfo(type=PortType.Display, name="in")}

    @property
    def display(self):
        return self._display

    @display.setter
    def display(self, display: DisplayHandle):
        self._display = display


def validate_edge(
    output_node: PipelineNode,
    output_port: PortInfo,
    input_node: PipelineNode,
    input_port: PortInfo,
):
    if output_port.type != input_port.type:
        raise Exception("Cannot connect a Meta port to a Data port")

    if not output_node.has(output_port, IOType.Out):
        raise Exception(
            f'The port "{output_port.name}" with type "{output_port.type}" '
            "does not exist on the output node."
        )

    if not input_node.has(input_port, IOType.In):
        raise Exception(
            f'The port "{input_port.name}" with type "{input_port.type}" '
            "does not exist on the input node."
        )


T = TypeVar("T")


def node_iter(
    nodes: Dict[IdType, PipelineNode], cls: Type[T]
) -> Generator[Tuple[IdType, T], None, None]:
    for node_id, node in nodes.items():
        if isinstance(node, cls):
            yield node_id, node


class Pipeline:
    def __init__(
        self, client: PlasmaClient, registry: Registry, id: Optional[IdType] = None
    ):
        self._id = unique_id(id)
        self.client = client
        self.registry = registry
        self.nodes: Dict[IdType, PipelineNode] = {}
        self.edges: Dict[IdType, PipelineEdge] = {}
        self.node_to_edges: Dict[IdType, Set[IdType]] = {}
        self.ports: Dict[str, Port] = {}
        self.observer: PipelineObserver = PipelineObserver()

    @property
    def id(self):
        return self._id

    @property
    def image_names(self):
        return set(
            node.operator.image_name
            for _, node in node_iter(self.nodes, OperatorNode)
            if node.operator is not None
        )

    def start_containers(self):
        self.registry.start_containers(self.image_names)

    def set_graph(self, nodes: Sequence[PipelineNode], edges: Sequence[PipelineEdge]):
        self_nodes: Dict[IdType, PipelineNode] = {}
        self_edges: Dict[IdType, PipelineEdge] = {}
        self_node_to_edges: Dict[IdType, Set[IdType]] = {}

        for node in nodes:
            self_nodes[node.id] = node
            self_node_to_edges[node.id] = set()

        for edge in edges:
            output_node = self_nodes.get(edge.output_node_id)
            if output_node is None:
                raise Exception(
                    f"The node {edge.output_node_id} referenced by the edge "
                    f"{edge.id} does not exist."
                )

            input_node = self_nodes.get(edge.input_node_id)
            if input_node is None:
                raise Exception(
                    f"The node {edge.input_node_id} referenced by the edge "
                    f"{edge.id} does not exist."
                )

            self_edges[edge.id] = edge

            validate_edge(output_node, edge.output_port, input_node, edge.input_port)

            self_node_to_edges.setdefault(output_node.id, set()).add(edge.id)
            self_node_to_edges.setdefault(input_node.id, set()).add(edge.id)

        # Verify that all the required operator input ports have a connection
        for node in nodes:

            required_input_ports = {
                port.name for port in node.inputs.values() if port.required
            }
            existing_input_ports = {
                self_edges[edge_id].input_port.name
                for edge_id in self_node_to_edges[node.id]
                if self_edges[edge_id].input_node_id == node.id
            }
            missing_input_ports = required_input_ports.difference(existing_input_ports)

            if missing_input_ports:
                raise Exception(
                    f"The node {node.id} has the following missing input "
                    f"connections: {missing_input_ports}"
                )

        self.nodes = self_nodes
        self.edges = self_edges
        self.node_to_edges = self_node_to_edges
        self.ports = {}

    def run(self):
        self.start_containers()

        for _, node in node_iter(self.nodes, DisplayNode):
            if node.display is not None:
                node.display.clear()

        all_operators = set(map(lambda t: t[0], node_iter(self.nodes, OperatorNode)))
        run_operators = set()

        self.observer.on_start(self)

        while all_operators.difference(run_operators):
            count = 0
            for operator_id, operator_node in node_iter(self.nodes, OperatorNode):
                if operator_id in run_operators:
                    continue

                input_edges: Sequence[PipelineEdge] = []
                output_edges: Sequence[PipelineEdge] = []
                for edge_id in self.node_to_edges[operator_id]:
                    edge = self.edges[edge_id]
                    if edge.input_node_id == operator_id:
                        input_edges.append(edge)
                    elif edge.output_node_id == operator_id:
                        output_edges.append(edge)

                do_run = True
                input_ports: Dict[PortKey, Port] = {}

                for edge in input_edges:
                    source_port_id = port_id(edge.output_node_id, edge.output_port.name)
                    port = self.ports.get(source_port_id)
                    if port is None:
                        do_run = False
                        break

                    input_ports[edge.input_port.name] = port

                if do_run:
                    self.observer.on_operator_start(self, operator_node)

                    operator = operator_node.operator

                    if operator is None:
                        err = Exception(
                            f"The operator node {operator_id} does not "
                            "have an associated operator handle."
                        )
                        self.observer.on_operator_error(self, operator_node, err)
                        self.observer.on_error(self, err)
                        raise err

                    if operator.location == LocationType.Local:
                        output_queue = f"/{self.id}_{operator_node.id}"
                    else:
                        output_queue = operator.input_queue

                    try:
                        output_ports: Dict[PortKey, Port] = operator.execute(
                            input_ports, output_queue
                        )
                    except Exception as err:
                        self.observer.on_operator_error(self, operator_node, err)
                        self.observer.on_error(self, err)
                        raise

                    for edge in output_edges:
                        # If there is a display output from this operator, render it
                        # immediately
                        if edge.output_port.type == PortType.Display:
                            port = output_ports[edge.output_port.name]
                            display_node: Any = self.nodes.get(edge.input_node_id)
                            if (
                                display_node is not None
                                and display_node.type == NodeType.Display
                                and display_node.display is not None
                            ):
                                display: DisplayHandle = display_node.display
                                display.add(edge.output_node_id, port)
                        # Otherwise save the port for use in a future iteration of the
                        # pipeline runner
                        else:
                            sink_port_id = port_id(
                                edge.output_node_id, edge.output_port.name
                            )
                            self.ports[sink_port_id] = output_ports[
                                edge.output_port.name
                            ]

                    run_operators.add(operator_id)
                    count = count + 1

                    self.observer.on_operator_complete(self, operator_node)

            if count == 0:
                raise Exception("The pipeline couldn't be resolved")

        self.observer.on_complete(self)


class PipelineObserver:
    def on_start(self, pipeline: Pipeline):
        pass

    def on_complete(self, pipeline: Pipeline):
        pass

    def on_error(self, pipeline: Pipeline, error: Any):
        pass

    def on_operator_start(self, pipeline: Pipeline, operator: OperatorNode):
        pass

    def on_operator_complete(self, pipeline: Pipeline, operator: OperatorNode):
        pass

    def on_operator_error(self, pipeline: Pipeline, operator: OperatorNode, error: Any):
        pass


def validate_port_type(type):
    valid_types = [
        PortType.Data,
        PortType.Display,
    ]

    if type not in valid_types:
        raise Exception(f"Unknown port type: {type}")

    return type


noop_display_factory: DisplayFactory = lambda id, type: NoopDisplayHandle(id, type)


def deserialize_pipeline(
    obj: JSONType,
    client: PlasmaClient,
    registry: Registry,
    display_factory: DisplayFactory = None,
):
    pipeline_json = PipelineJSON(**obj)
    _id = pipeline_json.id
    _nodes = pipeline_json.nodes
    _edges = pipeline_json.edges

    if display_factory is None:
        display_factory = noop_display_factory

    nodes: Sequence[PipelineNode] = []

    for _node in _nodes:
        node_type = _node.type

        if node_type == NodeType.Operator:
            _node = OperatorNodeJSON(**_node.dict())
            node = OperatorNode(_node.id)

            location = LocationType(_node.location)

            messenger = Messenger(location, client)

            _image_name = _node.image
            registry.register(_image_name, location)
            input_ports = registry.ports(_image_name, IOType.In)
            output_ports = registry.ports(_image_name, IOType.Out)
            name = registry.name(_image_name)
            params = _node.params
            input_queue = registry.input_queue(_image_name)

            operator = OperatorHandle(
                _image_name, name, input_queue, messenger, location
            )
            operator.parameters = params

            node.inputs = input_ports
            node.outputs = output_ports
            node.operator = operator

            nodes.append(node)

        elif node_type == NodeType.Display:
            _node = DisplayNodeJSON(**_node.dict())
            node = DisplayNode(_node.id, _node.display)

            display = display_factory(_node.id, _node.display)
            display._parameters = _node.params

            node.display = display

            nodes.append(node)

    edges: Sequence[PipelineEdge] = []

    for _edge in _edges:
        port_type = _edge.type
        from_node = _edge.start
        to_node = _edge.stop
        from_port = PortInfo(type=port_type, name=from_node.port)
        to_port = PortInfo(type=port_type, name=to_node.port)
        edge = PipelineEdge(from_node.id, from_port, to_node.id, to_port)

        edges.append(edge)

    pipeline = Pipeline(client, registry, _id)

    pipeline.set_graph(nodes, edges)

    return pipeline


def serialize_pipeline(pipeline: Pipeline) -> PipelineJSON:
    _nodes: Sequence[NodeJSON] = []

    for node_id, node in node_iter(pipeline.nodes, OperatorNode):
        operator = node.operator
        if operator is None:
            continue

        _node = OperatorNodeJSON(
            **{
                "id": node_id,
                "type": NodeType.Operator,
                "params": operator.parameters,
                "image": operator.image_name,
            }
        )

        _nodes.append(_node)

    for node_id, node in node_iter(pipeline.nodes, DisplayNode):
        display = node.display
        if display is None:
            continue

        _node = DisplayNodeJSON(
            **{
                "id": node_id,
                "type": NodeType.Display,
                "params": display.parameters,
                "display": display.type,
            }
        )

        _nodes.append(_node)

    _edges: Sequence[EdgeJSON] = []

    for edge in pipeline.edges.values():
        port_type = edge.output_port.type

        _edge = EdgeJSON(
            **{
                "type": port_type,
                "from": {"id": edge.output_node_id, "port": edge.output_port.name},
                "to": {"id": edge.input_node_id, "port": edge.input_port.name},
            }
        )

        _edges.append(_edge)

    return PipelineJSON(**{"nodes": _nodes, "edges": _edges, "id": pipeline.id})
