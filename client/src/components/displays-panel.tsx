import React from 'react';
import { useAppSelector } from '../app/hooks';
import { displaysSelector } from '../features/displays';
import { DisplayType } from '../types/pipeline';
import Display1DComponent from './display-1d';
import Display2DComponent from './display-2d';

type Props = {};

const DisplaysPanel: React.FC<Props> = () => {
  const displays = useAppSelector(displaysSelector.selectAll);
  return (
    <div className="displays-panel">
      {displays.map((display) => {
        return (
          <div className="display-container" key={display.id}>
            {display.type === DisplayType.OneD &&
              <Display1DComponent display={display}/>
            }
            {display.type === DisplayType.TwoD &&
              <Display2DComponent display={display}/>
            }
          </div>
        );
      })}
    </div>
  )
}

export default DisplaysPanel;
