import * as React from 'react';
import { OperatorDefinition }  from '../types/operator'
import { DisplayType } from '../types/pipeline';

interface OperatorPaletteItemWidgetProps {
	imageName: string
	operator: OperatorDefinition;
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

interface OperatorPaletteDisplayWidgetProps {
	displayType: DisplayType;
}

export const OperatorPaletteDisplayWidget: React.FC<OperatorPaletteDisplayWidgetProps> = (props) => {

  const opData = {
    displayType: props.displayType,
  }

  return (
    <div
      draggable={true}
      onDragStart={(event) => {
        event.dataTransfer.setData('display-node', JSON.stringify(opData));
      }}
      className="operator-palette-item display-palette-item">
      {`Display (${props.displayType})`}
    </div>
  );
}

interface PaletteWidgetProps {
	children: React.ReactNode;
}

export const PaletteWidget: React.FC<PaletteWidgetProps> = (props) => {
  return <div className="operator-pallet-container">{props.children}</div>;
}

interface OperatorPaletteProps {
  operators: {[image: string]: OperatorDefinition;} | undefined
}

const OperatorPalette: React.FC<OperatorPaletteProps> = (props) => {
  if (!props.operators) {
    return null;
  }

  return (
    <PaletteWidget>
      {
        [DisplayType.OneD, DisplayType.TwoD].map((displayType) => {
          return (
            <OperatorPaletteDisplayWidget key={displayType} displayType={displayType}/>
          );
        })
      }
      {
        Object.entries(props.operators).map(([imageName, operator]) => {
          return (
            <OperatorPaletteItemWidget key={imageName} operator={operator} imageName={imageName} />
          );
        })
      }
    </PaletteWidget>
  )
}

export default OperatorPalette;
