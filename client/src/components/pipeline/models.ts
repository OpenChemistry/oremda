import {
  DefaultLinkModel
} from '@projectstorm/react-diagrams';

import { NodeModel, NodeModelGenerics, LinkModel, PortModel, PortModelAlignment, PortModelGenerics, PortModelOptions } from '@projectstorm/react-diagrams-core';
import { BasePositionModelOptions, AbstractModelFactory, DeserializeEvent } from '@projectstorm/react-canvas-core';
import { NodeType, PipelineNode, PortType } from '../../types/pipeline';
import { OperatorDefinition } from '../../types/operator';
import { shortId } from '../../utils';

const inputPortId = (name: string) => `in://${name}`;
const outputPortId = (name: string) => `out://${name}`;

export interface OremdaPortModelOptions extends PortModelOptions {
	label: string;
	in: boolean;
  portType: PortType;
}

export interface OremdaPortModelGenerics extends PortModelGenerics {
	OPTIONS: OremdaPortModelOptions;
}

export class OremdaPortModel extends PortModel<OremdaPortModelGenerics> {
	constructor(options: OremdaPortModelOptions) {
		super({
			alignment: options.in ? PortModelAlignment.LEFT : PortModelAlignment.RIGHT,
			type: 'default',
			...options
		});
	}

	deserialize(event: DeserializeEvent<this>) {
		super.deserialize(event);
		this.options.in = event.data.in;
		this.options.label = event.data.label;
    this.options.portType = event.data.portType;
	}

	serialize() {
		return {
			...super.serialize(),
			in: this.options.in,
			label: this.options.label,
      portType: this.options.portType,
		};
	}

	link<T extends LinkModel>(port: PortModel, factory?: AbstractModelFactory<T>): T {
		let link = this.createLinkModel(factory);
		link.setSourcePort(this);
		link.setTargetPort(port);
		return link as T;
	}

	canLinkToPort(port: PortModel): boolean {
		if (port instanceof OremdaPortModel) {
			return this.options.in !== port.getOptions().in;
		}
		return true;
	}

	createLinkModel(factory?: AbstractModelFactory<LinkModel>): LinkModel {
		let link = super.createLinkModel();
		if (!link && factory) {
			return factory.generateModel({});
		}
		return link || new DefaultLinkModel();
	}
}

export interface OremdaNodeModelOptions extends BasePositionModelOptions {
	name: string;
	color: string;
}

export interface OremdaNodeModelGenerics extends NodeModelGenerics {
	OPTIONS: OremdaNodeModelOptions;
}

export class OremdaNodeModel extends NodeModel<OremdaNodeModelGenerics> {
  protected portsIn: {[id: string]: OremdaPortModel};
  protected portsOut: {[id: string]: OremdaPortModel};
  public pipelineNode: PipelineNode;

  constructor(node: PipelineNode, definition?: OperatorDefinition) {
    let name: string;
    let color: string;
    if (node.type === NodeType.Operator) {
      name = `${shortId(node.id)} - ${(node as any).image}`;
      color = 'rgb(0,192,255)';
    } else if (node.type === NodeType.Display) {
      name = `${shortId(node.id)} - Display (${(node as any).display})`;
      color = 'rgb(255,192,0)';
    } else {
      throw new Error('Unknown node type');
    }

    super({
        id: node.id,
        type: 'oremda',
        name,
        color,
    });
    this.portsOut = {};
    this.portsIn = {};

    if (node.type === NodeType.Operator && definition) {
      for (let [name, port] of Object.entries(definition.ports.input)) {
        this.addInPort(name, port.type);
      }

      for (let [name, port] of Object.entries(definition.ports.output)) {
        this.addOutPort(name, port.type);
      }
    } else if (node.type === NodeType.Display) {
      this.addInPort('in', PortType.Display);
    }
    this.pipelineNode = node;
  }

  doClone(lookupTable: {}, clone: any): void {
      clone.portsIn = {};
      clone.portsOut = {};
      super.doClone(lookupTable, clone);
  }

  removePort(port: OremdaPortModel): void {
    super.removePort(port);
    if (port.getOptions().in) {
      delete this.portsIn[port.getID()];
    } else {
      delete this.portsOut[port.getID()];
    }
  }

  addPort<T extends OremdaPortModel>(port: T): T {
    super.addPort(port);
    if (port.getOptions().in) {
      if (this.portsIn[port.getID()] === undefined) {
        this.portsIn[port.getID()] = port;
      }
    } else {
      if (this.portsOut[port.getID()] === undefined) {
        this.portsOut[port.getID()] = port;
      }
    }
    return port;
  }

  addInPort(label: string, type: PortType): OremdaPortModel {
    const portId = inputPortId(label);
    const p = new OremdaPortModel({
      in: true,
      id: portId,
      name: portId,
      label: label,
      alignment: PortModelAlignment.LEFT,
      portType: type,
    });
    return this.addPort(p);
  }

  addOutPort(label: string, type: PortType): OremdaPortModel {
    const portId = outputPortId(label);
    const p = new OremdaPortModel({
      in: false,
      id: portId,
      name: portId,
      label: label,
      alignment: PortModelAlignment.RIGHT,
      portType: type,
    });
    return this.addPort(p);
  }

  getInPort(label: string): OremdaPortModel | null {
    const portId = inputPortId(label);
    return this.getPort(portId) as any;
  }

  getOutPort(label: string): OremdaPortModel | null {
    const portId = outputPortId(label);
    return this.getPort(portId) as any;
  }

  deserialize(event: DeserializeEvent<this>) {
    super.deserialize(event);
    this.options.name = event.data.name;
    this.options.color = event.data.color;
    this.portsIn = (event.data.portsInOrder as string[]).reduce((tot, id) => {
      const port = this.getPortFromID(id);
      if (port) {
        tot[id] = port as any;
      }
      return tot;
    }, {} as typeof this.portsIn);
    this.portsOut = (event.data.portsOutOrder as string[]).reduce((tot, id) => {
      const port = this.getPortFromID(id);
      if (port) {
        tot[id] = port as any;
      }
      return tot;
    }, {} as typeof this.portsIn);
  }

  serialize(): any {
    return {
      ...super.serialize(),
      name: this.options.name,
      color: this.options.color,
      portsInOrder: Object.values(this.portsIn).map((port) => {
        return port.getID();
      }),
      portsOutOrder: Object.values(this.portsOut).map((port) => {
        return port.getID();
      })
    };
  }

  getInPorts() {
      return this.portsIn;
  }

  getOutPorts() {
      return this.portsOut;
  }
}

