from pydantic.main import BaseModel
from oremda.typing import EdgeJSON, JSONType, IdType, NodeJSON, PipelineJSON, PortKey
from typing import Optional, Dict, Sequence, Set
from oremda.operator import OperatorHandle
from oremda.utils.id import unique_id, port_id
from oremda.utils.types import bool_from_str
from oremda.typing import PortType, NodeType, IOType
from oremda.registry import Registry
from oremda.shared_resources import Client as MemoryClient, DataArray

class PortInfo:
    def __init__(self, port_type: PortType, name: PortKey, required: bool = False):
        self.type = port_type
        self.name = name
        self.required = required

    def __eq__(self, other: 'PortInfo'):
        return self.type == other.type and self.name == other.name

class PipelineEdge:
    def __init__(
        self,
        output_node_id: IdType,
        output_port: PortInfo,
        input_node_id: IdType,
        input_port: PortInfo,
        id: Optional[IdType]=None
    ):
        self.id = unique_id(id)
        self.output_node_id = output_node_id
        self.input_node_id = input_node_id
        self.output_port = output_port
        self.input_port = input_port

class PipelineNode:
    def __init__(self, t: NodeType, id: Optional[IdType]=None):
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

def validate_edge(output_node: PipelineNode, output_port: PortInfo, input_node: PipelineNode, input_port: PortInfo):
    if output_port.type != input_port.type:
        raise Exception('Cannot connect a Meta port to a Data port')

    if not output_node.has(output_port, IOType.Out):
        raise Exception(f'The port "{output_port.name}" with type "{output_port.type}" does not exist on the output node.')

    if not input_node.has(input_port, IOType.In):
        raise Exception(f'The port "{input_port.name}" with type "{input_port.type}" does not exist on the input node.')

def node_iter(nodes: Dict[IdType, PipelineNode], type: NodeType):
    for node_id, node in nodes.items():
        if node.type == type:
            yield node_id, node


class Pipeline:
    def __init__(self, client: MemoryClient, registry: Registry):
        self.client = client
        self.registry = registry
        self.nodes: Dict[IdType, OperatorNode] = {}
        self.edges: Dict[IdType, PipelineEdge] = {}
        self.node_to_edges: Dict[IdType, Set[IdType]] = {}
        self.data: Dict[str, DataArray] = {}
        self.meta: Dict[str, JSONType] = {}

    def set_graph(self, nodes: Sequence[OperatorNode], edges: Sequence[PipelineEdge]):
        self_nodes: Dict[IdType, OperatorNode] = {}
        self_edges: Dict[IdType, PipelineEdge] = {}
        self_node_to_edges: Dict[IdType, Set[IdType]] = {}

        for node in nodes:
            self_nodes[node.id] = node
            self_node_to_edges[node.id] = set()

        for edge in edges:
            output_node = self_nodes.get(edge.output_node_id)
            if output_node is None:
                raise Exception(f"The node {edge.output_node_id} referenced by the edge {edge.id} does not exist.")

            input_node = self_nodes.get(edge.input_node_id)
            if input_node is None:
                raise Exception(f"The node {edge.input_node_id} referenced by the edge {edge.id} does not exist.")

            self_edges[edge.id] = edge

            validate_edge(output_node, edge.output_port, input_node, edge.input_port)

            self_node_to_edges.setdefault(output_node.id, set()).add(edge.id)
            self_node_to_edges.setdefault(input_node.id, set()).add(edge.id)

        # Verify that all the required operator input ports have a connection
        for node in nodes:

            required_input_ports = {port.name for port in node.inputs.values() if port.required}
            existing_input_ports = {self_edges[edge_id].input_port.name for edge_id in self_node_to_edges[node.id] if self_edges[edge_id].input_node_id == node.id}
            missing_input_ports = required_input_ports.difference(existing_input_ports)

            if missing_input_ports:
                raise Exception(f"The node {node.id} has the following missing input connections: {missing_input_ports}")

        self.nodes = self_nodes
        self.edges = self_edges
        self.node_to_edges = self_node_to_edges
        self.data = {}
        self.meta = {}

    def run(self):
        all_operators = set(
            map(
                lambda t: t[0],
                self.nodes.items()
            )
        )
        run_operators = set()

        while all_operators.difference(run_operators):
            count = 0
            for operator_id, operator_node in self.nodes.items():
                if operator_id in run_operators:
                    continue

                input_edges = []
                output_edges = []
                for edge_id in self.node_to_edges[operator_id]:
                    edge = self.edges[edge_id]
                    if edge.input_node_id == operator_id:
                        input_edges.append(edge)
                    elif edge.output_node_id == operator_id:
                        output_edges.append(edge)

                do_run = True
                input_data = {}
                input_meta = {}

                for edge in input_edges:
                    source_port_id = port_id(edge.output_node_id, edge.output_port.name)

                    if edge.output_port.type == PortType.Data:
                        data_dict = self.data
                        input_dict = input_data
                    else:
                        data_dict = self.meta
                        input_dict = input_meta

                    d = data_dict.get(source_port_id)
                    if d is None:
                        do_run = False
                        break

                    input_dict[edge.input_port.name] = d

                if do_run:
                    operator = operator_node.operator

                    if operator is None:
                        raise Exception(f"The operator node {operator_id} does not have an associated operator handle.")

                    # Ensure an instance of this operator is running
                    if not self.registry.running(operator.image_name):
                        self.registry.run(operator.image_name)

                    output_meta, output_data = operator.execute(input_meta, input_data)

                    for edge in output_edges:
                        sink_port_id = port_id(edge.output_node_id, edge.output_port.name)

                        if edge.output_port.type == PortType.Data:
                            self.data[sink_port_id] = output_data[edge.output_port.name]
                        else:
                            self.meta[sink_port_id] = output_meta[edge.output_port.name]

                    run_operators.add(operator_id)
                    count = count + 1

            if count == 0:
                raise Exception("The pipeline couldn't be resolved")

def validate_port_type(type):
    valid_types = [
        PortType.Data,
        PortType.Meta,
    ]

    if type not in valid_types:
        raise Exception(f'Unknown port type: {type}')

    return type

def deserialize_pipeline(obj: JSONType, client: MemoryClient, registry: Registry):
    pipeline_json = PipelineJSON(**obj)
    _nodes = pipeline_json.nodes
    _edges = pipeline_json.edges

    nodes: Sequence[OperatorNode] = []

    for _node in _nodes:
        node = OperatorNode(_node.id)

        _image_name = _node.image
        _ports = registry.ports(_image_name)
        _input_ports = _ports.get('input', {})
        _output_ports = _ports.get('output', {})
        _queue_name = registry.name(_image_name)
        _params = _node.params

        input_ports = {}
        for name, port in _input_ports.items():
            port_type = validate_port_type(port.get('type'))
            required = bool_from_str(port.get('required', 'true'))
            input_ports[name] = PortInfo(port_type, name, required)

        output_ports = {}
        for name, port in _output_ports.items():
            port_type = validate_port_type(port.get('type'))
            output_ports[name] = PortInfo(port_type, name)

        params = {}
        for name, value in _params.items():
            params[name] = value

        operator = OperatorHandle(_image_name, _queue_name, client)
        operator.parameters = params

        node.inputs = input_ports
        node.outputs = output_ports
        node.operator = operator

        nodes.append(node)

    edges: Sequence[PipelineEdge] = []

    for _edge in _edges:
        port_type = _edge.type
        from_node = _edge.start
        to_node = _edge.stop
        from_port = PortInfo(port_type, from_node.port)
        to_port = PortInfo(port_type, to_node.port)
        edge = PipelineEdge(from_node.id, from_port, to_node.id, to_port)

        edges.append(edge)

    pipeline = Pipeline(client, registry)

    pipeline.set_graph(nodes, edges)

    return pipeline

def serialize_pipeline(pipeline: Pipeline) -> PipelineJSON:
    _nodes: Sequence[NodeJSON] = []

    for node in pipeline.nodes.values():
        operator = node.operator
        if operator is None:
            continue

        _params = {}
        for name, value in operator.parameters.items():
            _params[name] = value

        _node = NodeJSON(**{
            'id': node.id,
            'image': operator.image_name,
            'params': _params
        })

        _nodes.append(_node)

    _edges: Sequence[EdgeJSON] = []

    for edge in pipeline.edges.values():
        port_type = edge.output_port.type

        _edge = EdgeJSON(**{
            'type': port_type,
            'from': {
                'id': edge.output_node_id,
                'port': edge.output_port.name
            },
            'to': {
                'id': edge.input_node_id,
                'port': edge.input_port.name
            }
        })

        _edges.append(_edge)

    return PipelineJSON(**{'nodes': _nodes, 'edges': _edges})
