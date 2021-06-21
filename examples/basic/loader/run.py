import numpy as np

from oremda import Client as OremdaClient
from oremda import OperatorHandle

import oremda.pipeline
import oremda.source
from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH
from oremda.utils.plasma import start_plasma_store

meta_port_info = oremda.pipeline.PortInfo(oremda.pipeline.PortType.Meta, 'meta')
data_port_info = oremda.pipeline.PortInfo(oremda.pipeline.PortType.Data, 'scalars')

source_node_0 = oremda.pipeline.SourceNode()
source_node_0.outputs = {
    meta_port_info.name: meta_port_info,
    data_port_info.name: data_port_info,
}

operator_node_0 = oremda.pipeline.OperatorNode()
operator_node_0.inputs = {
    meta_port_info.name: meta_port_info,
    data_port_info.name: data_port_info,
}
operator_node_0.outputs = {
    meta_port_info.name: meta_port_info,
    data_port_info.name: data_port_info,
}

source_node_1 = oremda.pipeline.SourceNode()
source_node_1.outputs = {
    meta_port_info.name: meta_port_info,
    data_port_info.name: data_port_info,
}

operator_node_1 = oremda.pipeline.OperatorNode()
operator_node_1.inputs = {
    meta_port_info.name: meta_port_info,
    data_port_info.name: data_port_info,
}
operator_node_1.outputs = {
    meta_port_info.name: meta_port_info,
    data_port_info.name: data_port_info,
}

source_node_2 = oremda.pipeline.SourceNode()
source_node_2.outputs = {
    meta_port_info.name: meta_port_info,
    data_port_info.name: data_port_info,
}

view_node_0 = oremda.pipeline.OperatorNode()
view_node_0.inputs = {
    meta_port_info.name: meta_port_info,
    data_port_info.name: data_port_info,
}

view_node_1 = oremda.pipeline.OperatorNode()
view_node_1.inputs = {
    meta_port_info.name: meta_port_info,
    data_port_info.name: data_port_info,
}

view_node_2 = oremda.pipeline.OperatorNode()
view_node_2.inputs = {
    meta_port_info.name: meta_port_info,
    data_port_info.name: data_port_info,
}

meta_edge_0 = oremda.pipeline.PipelineEdge(source_node_0.id, meta_port_info, operator_node_0.id, meta_port_info)
data_edge_0 = oremda.pipeline.PipelineEdge(source_node_0.id, data_port_info, operator_node_0.id, data_port_info)

meta_edge_1 = oremda.pipeline.PipelineEdge(operator_node_0.id, meta_port_info, source_node_1.id, meta_port_info)
data_edge_1 = oremda.pipeline.PipelineEdge(operator_node_0.id, data_port_info, source_node_1.id, data_port_info)

meta_edge_2 = oremda.pipeline.PipelineEdge(source_node_1.id, meta_port_info, operator_node_1.id, meta_port_info)
data_edge_2 = oremda.pipeline.PipelineEdge(source_node_1.id, data_port_info, operator_node_1.id, data_port_info)

meta_edge_3 = oremda.pipeline.PipelineEdge(operator_node_1.id, meta_port_info, source_node_2.id, meta_port_info)
data_edge_3 = oremda.pipeline.PipelineEdge(operator_node_1.id, data_port_info, source_node_2.id, data_port_info)

meta_edge_4 = oremda.pipeline.PipelineEdge(source_node_0.id, meta_port_info, view_node_0.id, meta_port_info)
data_edge_4 = oremda.pipeline.PipelineEdge(source_node_0.id, data_port_info, view_node_0.id, data_port_info)

meta_edge_5 = oremda.pipeline.PipelineEdge(source_node_1.id, meta_port_info, view_node_1.id, meta_port_info)
data_edge_5 = oremda.pipeline.PipelineEdge(source_node_1.id, data_port_info, view_node_1.id, data_port_info)

meta_edge_6 = oremda.pipeline.PipelineEdge(source_node_2.id, meta_port_info, view_node_2.id, meta_port_info)
data_edge_6 = oremda.pipeline.PipelineEdge(source_node_2.id, data_port_info, view_node_2.id, data_port_info)

nodes = [
    source_node_0,
    operator_node_0,
    source_node_1,
    operator_node_1,
    source_node_2,
    view_node_0,
    view_node_1,
    view_node_2,
]

edges = [
    meta_edge_0,
    data_edge_0,
    meta_edge_1,
    data_edge_1,
    meta_edge_2,
    data_edge_2,
    meta_edge_3,
    data_edge_3,
    meta_edge_4,
    data_edge_4,
    meta_edge_5,
    data_edge_5,
    meta_edge_6,
    data_edge_6,
]

roots = [
    source_node_0.id
]

kwargs = {
    'memory': 50000000,
    'socket_path': DEFAULT_PLASMA_SOCKET_PATH,
}

with start_plasma_store(**kwargs):
    client = OremdaClient(DEFAULT_PLASMA_SOCKET_PATH)

    pipeline = oremda.pipeline.Pipeline(client)

    source = oremda.source.Source(client)

    source.set(meta_port_info, {'foo': 123})

    array = oremda.source.DataArray(client)
    array.data = np.array([0, 1, 2, 3])
    source.set(data_port_info, array)
    source_node_0.source = source

    operator = OperatorHandle('add', client)
    operator.parameters = {'value': 3}
    operator_node_0.operator = operator

    operator = OperatorHandle('add', client)
    operator.parameters = {'value': -5}
    operator_node_1.operator = operator

    operator = OperatorHandle('view', client)
    operator.parameters = {}
    view_node_0.operator = operator

    operator = OperatorHandle('view', client)
    operator.parameters = {}
    view_node_1.operator = operator

    operator = OperatorHandle('view', client)
    operator.parameters = {}
    view_node_2.operator = operator

    pipeline.set_graph(nodes, edges, roots)
    pipeline.run()
