import { PortType } from './pipeline';

export type PortLabels = {
    type: PortType
    required: boolean
}

export type PortsLabels = {
    input: {[key: string]: PortLabels;};
    output: {[key: string]: PortLabels;};
}

export type ParamLabels = {
  type: string;
  required: boolean;
}

export type OperatorDefinition = {
  name: string;
  ports: PortsLabels;
  params: {[key: string]: ParamLabels;};
}
