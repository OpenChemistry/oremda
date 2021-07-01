import numpy as np

from oremda import Client as OremdaClient
from oremda import OperatorHandle

import oremda.pipeline
from oremda.pipeline import PipelineEdge
from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH
from oremda.utils.plasma import start_plasma_store

eloss_port_info = oremda.pipeline.PortInfo(oremda.pipeline.PortType.Data, 'eloss')
spec_port_info = oremda.pipeline.PortInfo(oremda.pipeline.PortType.Data, 'spec')
elossbg_port_info = oremda.pipeline.PortInfo(oremda.pipeline.PortType.Data, 'eloss_bg')
background_port_info = oremda.pipeline.PortInfo(oremda.pipeline.PortType.Data, 'background')
x0_port_info = oremda.pipeline.PortInfo(oremda.pipeline.PortType.Data, 'x0')
y0_port_info = oremda.pipeline.PortInfo(oremda.pipeline.PortType.Data, 'y0')
x1_port_info = oremda.pipeline.PortInfo(oremda.pipeline.PortType.Data, 'x1')
y1_port_info = oremda.pipeline.PortInfo(oremda.pipeline.PortType.Data, 'y1')

reader_node = oremda.pipeline.OperatorNode()
reader_node.outputs = {
    eloss_port_info.name: eloss_port_info,
    spec_port_info.name: spec_port_info,
}

plot_node_0 = oremda.pipeline.OperatorNode()
plot_node_0.inputs = {
    x0_port_info.name: x0_port_info,
    y0_port_info.name: y0_port_info,
}

background_fit_node = oremda.pipeline.OperatorNode()
background_fit_node.inputs = {
    eloss_port_info.name: eloss_port_info,
    spec_port_info.name: spec_port_info,
}
background_fit_node.outputs = {
    eloss_port_info.name: eloss_port_info,
    background_port_info.name: background_port_info,
}

plot_node_1 = oremda.pipeline.OperatorNode()
plot_node_1.inputs = {
    x0_port_info.name: x0_port_info,
    y0_port_info.name: y0_port_info,
    x1_port_info.name: x1_port_info,
    y1_port_info.name: y1_port_info,
}

subtract_node = oremda.pipeline.OperatorNode()
subtract_node.inputs = {
    eloss_port_info.name: eloss_port_info,
    spec_port_info.name: spec_port_info,
    elossbg_port_info.name: elossbg_port_info,
    background_port_info.name: background_port_info,
}
subtract_node.outputs = {
    eloss_port_info.name: eloss_port_info,
    spec_port_info.name: spec_port_info,
}

plot_node_2 = oremda.pipeline.OperatorNode()
plot_node_2.inputs = {
    x0_port_info.name: x0_port_info,
    y0_port_info.name: y0_port_info,
}

nodes = [
    reader_node,
    plot_node_0,
    background_fit_node,
    plot_node_1,
    subtract_node,
    plot_node_2,
]

edges = [
    # -> Reader

    # -> Plot_0
    PipelineEdge(reader_node.id, eloss_port_info, plot_node_0.id, x0_port_info),
    PipelineEdge(reader_node.id, spec_port_info, plot_node_0.id, y0_port_info),
    # -> Background fit
    PipelineEdge(reader_node.id, eloss_port_info, background_fit_node.id, eloss_port_info),
    PipelineEdge(reader_node.id, spec_port_info, background_fit_node.id, spec_port_info),
    # -> Plot_1
    PipelineEdge(reader_node.id, eloss_port_info, plot_node_1.id, x0_port_info),
    PipelineEdge(reader_node.id, spec_port_info, plot_node_1.id, y0_port_info),
    PipelineEdge(background_fit_node.id, eloss_port_info, plot_node_1.id, x1_port_info),
    PipelineEdge(background_fit_node.id, background_port_info, plot_node_1.id, y1_port_info),
    # -> Background subtraction
    PipelineEdge(reader_node.id, eloss_port_info, subtract_node.id, eloss_port_info),
    PipelineEdge(reader_node.id, spec_port_info, subtract_node.id, spec_port_info),
    PipelineEdge(background_fit_node.id, eloss_port_info, subtract_node.id, elossbg_port_info),
    PipelineEdge(background_fit_node.id, background_port_info, subtract_node.id, background_port_info),
    # -> Plot_2
    PipelineEdge(subtract_node.id, eloss_port_info, plot_node_2.id, x0_port_info),
    PipelineEdge(subtract_node.id, spec_port_info, plot_node_2.id, y0_port_info),
]

kwargs = {
    'memory': 50000000,
    'socket_path': DEFAULT_PLASMA_SOCKET_PATH,
}

with start_plasma_store(**kwargs):
    client = OremdaClient(DEFAULT_PLASMA_SOCKET_PATH)

    pipeline = oremda.pipeline.Pipeline(client)

    operator = OperatorHandle('ncem_reader', client)
    operator.parameters = {'filename': '08_carbon.dm3'}
    reader_node.operator = operator

    operator = OperatorHandle('plot', client)
    operator.parameters = {'filename': 'spectrum.png', 'xLabel': 'eLoss (eV)', 'yLabel': ''}
    plot_node_0.operator = operator

    operator = OperatorHandle('background_fit', client)
    operator.parameters = {'start': 268, 'stop': 277}
    background_fit_node.operator = operator

    operator = OperatorHandle('plot', client)
    operator.parameters = {'filename': 'background.png', 'xLabel': 'eLoss (eV)', 'yLabel': ''}
    plot_node_1.operator = operator

    operator = OperatorHandle('subtract', client)
    operator.parameters = {'start': 268, 'stop': 430}
    subtract_node.operator = operator

    operator = OperatorHandle('plot', client)
    operator.parameters = {'filename': 'subtracted.png', 'xLabel': 'eLoss (eV)', 'yLabel': ''}
    plot_node_2.operator = operator

    pipeline.set_graph(nodes, edges)
    pipeline.run()
