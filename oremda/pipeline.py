import json

import pyarrow.plasma as plasma
from oremda.constants import OREMDA_FINISHED_QUEUE
from oremda.constants import NodeType, PortType, IOType, TaskType
from oremda.utils.id import unique_id
import oremda.source

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
    def __init__(self, t, multi_input=False, multi_output=False, id=None):
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

class ReaderNode(PipelineNode):
    inputs = PipelineNode.inputs

    def __init__(self, id=None):
        super().__init__(NodeType.Reader, id)

    @inputs.setter
    def inputs(self, inputs):
        raise Exception('A Reader can only have output ports')

class SourceNode(PipelineNode):
    inputs = PipelineNode.inputs
    outputs = PipelineNode.outputs

    def __init__(self, multi_output=True, id=None):
        super().__init__(NodeType.Source, id)
        self._source = None

    @property
    def source(self):
        return self._source
    
    @source.setter
    def source(self, source):
        self._source = source
    
    @inputs.setter
    def inputs(self, inputs):
        self.outputs = inputs

    @outputs.setter
    def outputs(self, outputs):
        self._outputs = outputs
        self._inputs = outputs

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
        
    def set_graph(self, nodes, edges, roots):
        self_nodes = {}
        self_edges = {}
        self_roots = roots
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

        if len(self_roots) < 1:
            raise Exception("Please specify at least one root node")

        for root_id in self_roots:
            root_node = self_nodes.get(root_id)
            if root_node is None:
                raise Exception(f"The root node {root_id} does not exist.")
            elif root_node.type != NodeType.Source:
                raise Exception("Only a Source node can be a root node.")

        self.nodes = self_nodes
        self.edges = self_edges
        self.roots = self_roots
        self.node_to_edges = self_node_to_edges

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
                    input_source_node = self.nodes[edge.output_node_id]
                    input_source = input_source_node.source
                    if input_source is None:
                        do_run = False
                        break

                    source_port = edge.output_port
                    operator_port = edge.input_port
                    if input_source.has(source_port):
                        if source_port.type == PortType.Data:
                            input_data[operator_port.name] = input_source.get(source_port)
                        else:
                            input_meta[operator_port.name] = input_source.get(source_port)
                    else:
                        do_run = False
                        break

                if do_run:
                    operator = operator_node.operator

                    if operator is None:
                        raise Exception(f"The operator node {operator_id} does not have an associated operator handle.")

                    output_meta, output_data = operator.execute(input_meta, input_data)

                    for edge in output_edges:
                        output_source_node = self.nodes[edge.input_node_id]
                        output_source = output_source_node.source
                        if output_source is None:
                            output_source = oremda.source.Source(self.client)
                            output_source_node.source = output_source

                        source_port = edge.input_port
                        operator_port = edge.output_port

                        if operator_port.type == PortType.Data:
                            output_source.set(source_port, output_data[operator_port.name])
                        else:
                            output_source.set(source_port, output_meta[operator_port.name])

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
