import { IdType } from '.';

export enum NodeType {
  Operator = 'operator',
  Display = 'display',
}

export enum DisplayType {
  OneD = '1D',
  TwoD = '2D',
  ThreeD = '3D',
}

export enum PortType {
  Data = 'data',
  Display = 'display',
}

export type BasePipelineNode = {
  id: IdType;
  type: NodeType;
  params: any;
}

export interface OperatorNode extends BasePipelineNode {
  image: string;
};

export interface DisplayNode extends BasePipelineNode {
  display: DisplayType;
};

export type PipelineNode = OperatorNode | DisplayNode;

export function isDisplayNode(node: PipelineNode): node is DisplayNode {
  return node.type === NodeType.Display;
}

export type PipelineEdge = {
  type: PortType;
  from: {
    id: IdType;
    port: string;
  };
  to: {
    id: IdType;
    port: string;
  }
}

export type Pipeline = {
  id: IdType;
  nodes: PipelineNode[];
  edges: PipelineEdge[];
}

export type Display = {
  id: IdType;
  type: DisplayType;
}
