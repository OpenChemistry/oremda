import { OremdaNodeWidget } from './widgets';
import { OremdaNodeModel } from './models';
import React from 'react';
import { AbstractReactFactory } from '@projectstorm/react-canvas-core';
import { DiagramEngine } from '@projectstorm/react-diagrams-core';
import { DisplayType, NodeType } from '../../types/pipeline';

export class OremdaNodeFactory extends AbstractReactFactory<OremdaNodeModel, DiagramEngine> {
	constructor() {
		super('oremda');
	}

	generateReactWidget(event: any): JSX.Element {
		return <OremdaNodeWidget engine={this.engine} node={event.model} />;
	}

	generateModel(event: any) {
		return new OremdaNodeModel({id: '', type: NodeType.Operator, params: {}, display: DisplayType.OneD});
	}
}
