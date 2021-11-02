import React from 'react';
import { useAppSelector } from '../app/hooks';
import { displaysSelector } from '../features/displays';
import { DisplayType } from '../types/pipeline';
import { shortId } from '../utils';
import RemoteDisplayComponent from './display-remote';

type Props = {};

// Optional predefined layouts (ascending order of n)
const DISPLAY_LAYOUTS = [
  {n: 1, rows: 1, cols: 1},
  {n: 2, rows: 1, cols: 2},
  {n: 4, rows: 2, cols: 2},
  {n: 6, rows: 2, cols: 3},
  {n: 9, rows: 3, cols: 3},
  {n: 12, rows: 3, cols: 4},
  {n: 16, rows: 4, cols: 4},
];

function getLayout(n: number){
  // TODO: Binary search
  for (let layout of DISPLAY_LAYOUTS) {
    if (layout.n >= n) {
      return layout;
    }
  }

  let cols = Math.floor(Math.sqrt(n));
  cols = cols * cols < n ? cols + 1 : cols;

  let rows = Math.floor(n / cols);
  rows = cols * rows < n ? rows + 1 : rows;

  return { n: rows * cols, rows, cols }
}

const DisplaysPanel: React.FC<Props> = () => {
  const displays = useAppSelector(displaysSelector.selectAll);

  const {rows, cols} = getLayout(displays.length);

  return (
    <div className="displays-panel">
      {displays.map((display, i) => {
        const col = i % cols;
        const row = Math.floor(i / cols);
        const left = `${100 * col / cols}%`;
        const top = `${100 * row / rows}%`;
        const width = `${100 / cols}%`;
        const height = `${100 / rows}%`;
        return (
          <div className="display-container" style={{left, top, width, height}} key={display.id}>
            {display.type === DisplayType.OneD &&
              <RemoteDisplayComponent display={display}/>
            }
            {display.type === DisplayType.TwoD &&
              <RemoteDisplayComponent display={display}/>
            }
            <span className='display-label'>{`${shortId(display.id)} - (${display.type})`}</span>
          </div>
        );
      })}
    </div>
  )
}

export default DisplaysPanel;
