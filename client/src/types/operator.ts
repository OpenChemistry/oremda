import { PortType } from './pipeline';

export type PortLabels = {
    type: PortType
    required: boolean
}

export type PortsLabels = {
    input: Map<string, PortLabels>
    output: Map<string, PortLabels>
}

export type ParamLabels = {
  type: string;
  required: boolean;
}

export type Operator = {
  name: string;
  ports: PortsLabels
  params: Map<string, ParamLabels>
}
