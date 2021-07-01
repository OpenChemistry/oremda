import json

import pyarrow.plasma as plasma
from oremda.constants import OREMDA_FINISHED_QUEUE, DEFAULT_PLASMA_SOCKET_PATH
from oremda.constants import NodeType, PortType, IOType, TaskType
from oremda.operator import OperatorHandle
from oremda.utils.id import unique_id, port_id

class PortInfo:
    def __init__(self, port_type, name):
        self.type = port_type
        self.name = name
    
    def __eq__(self, other):
        return self.type == other.type and self.name == other.name


class InputInfo:
    def __init__(self, required=True):
        self.required = required

class OutputInfo:
    def __init__(self):
        pass

class PipelineEdge:
    def __init__(self, output_node_id, output_port, input_node_id, input_port, id=None):
        self.id = unique_id(id)
        self.output_node_id = output_node_id
        self.input_node_id = input_node_id
        self.output_port = output_port
        self.input_port = input_port

class PipelineNode:
    def __init__(self, t, id=None):
        self._id = unique_id(id)
        self._type = t
        self._inputs = {}
        self._outputs = {}

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
    def inputs(self, inputs):
        self._inputs = inputs

    @property
    def outputs(self):
        return self._outputs
    
    @outputs.setter
    def outputs(self, outputs):
        self._outputs = outputs
    
    def has(self, port, io):
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
        self._operator = None
    
    @property
    def operator(self):
        return self._operator
    
    @operator.setter
    def operator(self, operator):
        self._operator = operator

def validate_edge(output_node, output_port, input_node, input_port):
    if output_port.type != input_port.type:
        raise Exception('Cannot connect a Meta port to a Data port')

    port_type = output_port.type

    if not output_node.has(output_port, IOType.Out):
        raise Exception(f'The port "{output_port.name}" with type "{output_port.type}" does not exist on the output node.')
    
    if not input_node.has(input_port, IOType.In):
        raise Exception(f'The port "{input_port.name}" with type "{input_port.type}" does not exist on the input node.')

def node_iter(nodes, type):
    for node_id, node in nodes.items():
        if node.type == type:
            yield node_id, node


class Pipeline:
    def __init__(self, client):
        self.client = client
        self.nodes = {}
        self.edges = {}
        self.node_to_edges = {}
        self.data = {}
        self.meta = {}
        
    def set_graph(self, nodes, edges):
        self_nodes = {}
        self_edges = {}
        self_node_to_edges = {}

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

        self.nodes = self_nodes
        self.edges = self_edges
        self.node_to_edges = self_node_to_edges
        self.data = {}
        self.meta = {}

    def run(self):
        all_operators = set(
            map(
                lambda t: t[0],
                node_iter(self.nodes, NodeType.Operator)
            )
        )
        run_operators = set()

        while len(all_operators.difference(run_operators)) > 0:
            count = 0
            for operator_id, operator_node in node_iter(self.nodes, NodeType.Operator):
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

    def _terminate_operators(self, operators):
        message = json.dumps({'task': TaskType.Terminate})
        names = set(x['name'] for x in operators)
        for name in names:
            with self.client.open_queue(f'/{name}') as queue:
                queue.send(message)

    def _create_queues(self, operators):
        with self.client.open_queue(OREMDA_FINISHED_QUEUE, create=True, reuse=True) as done_queue:
            pass

def validate_port_type(type):
    if type == PortType.Data:
        return PortType.Data
    elif type == PortType.Meta:
        return PortType.Meta
    else:
        raise Exception(f'Unknown port type: {type}')

def deserialize_pipeline(obj, client):
    _nodes = obj.get('nodes', [])
    _edges = obj.get('edges', [])

    nodes = []

    for _node in _nodes:
        node = OperatorNode(_node.get('id'))

        _input_ports = _node.get('ports', {}).get('input', {})
        _output_ports = _node.get('ports', {}).get('output', {})
        _params = _node.get('params', {})
        _queue_name = _node['queue']

        input_ports = {}
        for name, port in _input_ports.items():
            port_type = validate_port_type(port.get('type'))
            input_ports[name] = PortInfo(port_type, name)

        output_ports = {}
        for name, port in _output_ports.items():
            port_type = validate_port_type(port.get('type'))
            output_ports[name] = PortInfo(port_type, name)

        params = {}
        for name, value in _params.items():
            params[name] = value

        operator = OperatorHandle(_queue_name, client)
        operator.parameters = params

        node.inputs = input_ports
        node.outputs = output_ports
        node.operator = operator

        nodes.append(node)

    edges = []

    for _edge in _edges:
        port_type = validate_port_type(_edge.get('type'))
        from_node = _edge['from']
        to_node = _edge['to']
        from_port = PortInfo(port_type, from_node['port'])
        to_port = PortInfo(port_type, to_node['port'])
        edge = PipelineEdge(from_node['id'], from_port, to_node['id'], to_port)

        edges.append(edge)

    pipeline = Pipeline(client)

    pipeline.set_graph(nodes, edges)

    return pipeline
