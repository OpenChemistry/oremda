import React from 'react';
import { useAppSelector } from '../app/hooks';
import OperatorPalette from './operator-palette';

type Props = {};

const OperatorsPanel: React.FC<Props> = () => {
  const operators = useAppSelector((state) => state.operators.operators);

  return (
    <div className="operators-panel">
      <h4>
        Operators
      </h4>
      <OperatorPalette operators={operators}/>
    </div>
  )
}

export default OperatorsPanel;
