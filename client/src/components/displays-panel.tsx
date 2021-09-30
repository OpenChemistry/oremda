import React from 'react';
import { useAppSelector } from '../app/hooks';
import { displaysSelector } from '../features/displays';
import { DisplayType } from '../types/pipeline';
import RemoteDisplayComponent from './display-remote';

type Props = {};

const DisplaysPanel: React.FC<Props> = () => {
  const displays = useAppSelector(displaysSelector.selectAll);
  return (
    <div className="displays-panel">
      {displays.map((display) => {
        return (
          <div className="display-container" key={display.id}>
            {display.type === DisplayType.OneD &&
              <RemoteDisplayComponent display={display}/>
            }
            {display.type === DisplayType.TwoD &&
              <RemoteDisplayComponent display={display}/>
            }
          </div>
        );
      })}
    </div>
  )
}

export default DisplaysPanel;
