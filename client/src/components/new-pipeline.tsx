import React, { useRef } from 'react';
import { PaletteWidget } from './operator-palette';
import { OperatorPaletteItemWidget } from './operator-palette';
import { CanvasWidget } from '@projectstorm/react-canvas-core';
import createEngine, {
	DefaultNodeModel,
	DiagramModel, DefaultPortModel
  } from '@projectstorm/react-diagrams';
import { Operator } from '../types/operator'
import { v4 as uuidv4 } from 'uuid';

type Props = {
	operators: Map<string, Operator> | undefined
};

export const NewPipelineWidget: React.FC<Props> = (props) => {

	const engine = useRef(createEngine());

	if (props.operators === undefined || engine.current === null) {
		return null;
	}

	const model = new DiagramModel();
	engine.current.setModel(model);

	return (
		<div className="new-pipeline-container">
			<div className="new-pipeline-container-header">
				<div className="title">New Pipeline</div>
			</div>
			<div className="new-pipeline-container-content">
				<PaletteWidget>
				{
					Array.from(props.operators, ([imageName, operator]) => {
						if (props.operators === undefined) {
							return null;
						}

						return (
							<OperatorPaletteItemWidget operator={operator} imageName={ imageName } />
						);
					})
				}
				</PaletteWidget>
				<div
				    className="new-pipeline-container-layer"
				    onDrop={(event) => {
						var opData = JSON.parse(event.dataTransfer.getData('operator-node'));
						var nodesCount = Object.keys(engine.current.getModel().getNodes()).length;

						var node: DefaultNodeModel | null = null;

						node = new DefaultNodeModel({
							name: `${nodesCount + 1} - ${opData.imageName}`,
							color: 'rgb(0,192,255)',
						  });

						// Add input ports
						for (const portName in opData.operator.ports.input) {
							const port = new DefaultPortModel({name: uuidv4(), label: portName, in: true});
							node.addPort(port);
						}

						// Add output ports
						for (const portName in opData.operator.ports.output) {
							const port = new DefaultPortModel({name: uuidv4(), label: portName, in: false, maximumLinks: 1});
							node.addPort(port);
						}

						var point = engine.current.getRelativeMousePoint(event);
						node.setPosition(point);
						engine.current.getModel().addNode(node);
						engine.current.repaintCanvas();
					}}
					onDragOver={(event) => {
						event.preventDefault();
					}}>

					{ <CanvasWidget className='pipeline-diagram' engine={engine.current} /> }

				</div>
			</div>
		</div>
	);
}
