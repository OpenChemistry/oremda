import * as React from 'react';
import { Operator }  from '../types/operator'

interface OperatorPaletteItemWidgetProps {
	imageName: string
	operator: Operator;
}

export const OperatorPaletteItemWidget: React.FC<OperatorPaletteItemWidgetProps> = (props) => {

		const opData = {
			imageName: props.imageName,
			operator: props.operator
		}

		return (
			<div
				draggable={true}
				onDragStart={(event) => {
					event.dataTransfer.setData('operator-node', JSON.stringify(opData));
				}}
				className="operator-palette-item">
				{props.imageName}
			</div>
		);
}

interface PaletteWidgetProps {
	children: React.ReactNode;
}

export const PaletteWidget: React.FC<PaletteWidgetProps> = (props) => {
		return <div>{props.children}</div>;
}
