import React from 'react';
import { DiagramEngine, PortWidget } from '@projectstorm/react-diagrams-core';
import { OremdaNodeModel, OremdaPortModel } from './models';
import styled from '@emotion/styled';
import { PortType } from '../../types/pipeline';

namespace S {
	export const Node = styled.div<{ background: string; selected: boolean }>`
		background-color: ${(p) => p.background};
		border-radius: 5px;
		font-family: sans-serif;
		color: white;
		border: solid 2px black;
		overflow: visible;
		font-size: 11px;
		border: solid 2px ${(p) => (p.selected ? 'rgb(0,192,255)' : 'black')};
		min-width: 150px;
	`;

	export const Title = styled.div`
		background: rgba(0, 0, 0, 0.3);
		display: flex;
		white-space: nowrap;
		justify-items: center;
	`;

	export const TitleName = styled.div`
		flex-grow: 1;
		padding: 5px 5px;
	`;

	export const Ports = styled.div`
		display: flex;
		background-image: linear-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.2));
	`;

	export const PortsContainer = styled.div`
		flex-grow: 1;
		display: flex;
		flex-direction: column;
		&:first-of-type {
			margin-right: 10px;
		}
		&:only-child {
			margin-right: 0px;
		}
	`;

  export const Params = styled.div`
    flex-grow: 1;
    padding: 5px;
    color: black;
		background-image: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5));
	`;

  export const ParamContainer = styled.div``;
  export const ParamName = styled.span`
    font-weight: 700;
  `;
  export const ParamValue = styled.span``;
}

export interface NodeProps {
	node: OremdaNodeModel;
	engine: DiagramEngine;
}

function isNil(value: any) {
	return value !== undefined && value !== null;
}

/**
 * Default node that models the DefaultNodeModel. It creates two columns
 * for both all the input ports on the left, and the output ports on the right.
 */
export class OremdaNodeWidget extends React.Component<NodeProps> {
	generatePort = (port: OremdaPortModel) => {
		return <OremdaPortLabel engine={this.props.engine} port={port} key={port.getID()} />;
	};

	render() {
		return (
			<S.Node
				data-default-node-name={this.props.node.getOptions().name}
				selected={this.props.node.isSelected()}
				background={this.props.node.getOptions().color}>
				<S.Title>
					<S.TitleName>{this.props.node.getOptions().name}</S.TitleName>
				</S.Title>
				<S.Ports>
					<S.PortsContainer>{Object.values(this.props.node.getInPorts()).map(this.generatePort)}</S.PortsContainer>
					<S.PortsContainer>{Object.values(this.props.node.getOutPorts()).map(this.generatePort)}</S.PortsContainer>
				</S.Ports>
        <S.Params>
          {Object.entries(this.props.node.pipelineNode.params).map(([key, value]) => {
            return (
              <S.ParamContainer key={key}>
                <S.ParamName>{`${key}: `}</S.ParamName>
                <S.ParamValue>{(isNil(value) ? value : '' as any).toString()}</S.ParamValue>
              </S.ParamContainer>
            )
          })}
        </S.Params>
			</S.Node>
		);
	}
}


export interface PortLabelProps {
	port: OremdaPortModel;
	engine: DiagramEngine;
}

namespace S {
	export const PortLabel = styled.div`
		display: flex;
		margin-top: 1px;
		align-items: center;
	`;

	export const InLabel = styled.div`
		padding: 0 5px;
		flex-grow: 1;
	`;

	export const OutLabel = styled.div`
		padding: 0 5px;
		flex-grow: 1;
		text-align: right;
	`;

	export const Port = styled.div`
		width: 15px;
		height: 15px;
		background: rgba(255, 255, 255, 0.1);
		&:hover {
			background: rgb(192, 255, 0);
		}
	`;
}

export class OremdaPortLabel extends React.Component<PortLabelProps> {
	render() {
		const portType = this.props.port.getOptions().portType;
		const isIn = this.props.port.getOptions().in;

		let className = 'base-port ';
		if (portType === PortType.Display) {
			className += 'display-port';
		} else if (portType === PortType.Binary) {
			className += 'display-binary';
		} else {
			className += 'data-port';
		}

		const port = (
			<PortWidget engine={this.props.engine} port={this.props.port} className={className}>
				<S.Port />
			</PortWidget>
		);

		const Label = isIn ? S.InLabel : S.OutLabel;
		const label = <Label>{this.props.port.getOptions().label}</Label>;

		return (
			<S.PortLabel>
				{this.props.port.getOptions().in ? port : label}
				{this.props.port.getOptions().in ? label : port}
			</S.PortLabel>
		);
	}
}
