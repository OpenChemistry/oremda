import React, { useEffect, useRef } from 'react';

import Plotly from 'plotly.js';

import { useAppSelector } from '../app/hooks';
import { IdType } from '../types';
import { Display } from '../types/pipeline';

type Props = {
    display: Display;
}

class DisplayHandle1D {
  container: React.RefObject<HTMLDivElement>;
  data: any;

  constructor(container: React.RefObject<HTMLDivElement>) {
    this.container = container;
    this.data = {};
  }

  addInput(sourceId: IdType, payload: any) {
    const { x, y, label } = payload;
    this.data[sourceId] = {x, y, name: label, mode: 'lines'}
  }

  removeInput(sourceId: IdType) {
    delete this.data[sourceId];
  }

  clearInputs() {
    this.data = {}
  }

  render() {
    if (this.container.current) {
      Plotly.newPlot(this.container.current, Object.values(this.data));
    }
  }
}

const Display1DComponent: React.FC<Props> = (props) => {
  const ws = useAppSelector((state) => state.notifications.ws);

  const container = useRef<HTMLDivElement>(null);

  const displayHandle = useRef(new DisplayHandle1D(container));

  useEffect(() => {
    if (!ws) {
      return;
    }

    const listener = (ev: MessageEvent) => {
      if (!displayHandle.current) {
        return;
      }

      const data = JSON.parse(ev.data);

      if (data.type !== '@@OREMDA') {
        return;
      }

      if (data.payload.displayId !== props.display.id) {
        return;
      }

      if (data.action === 'DISPLAY_ADD_INPUT') {
        const { sourceId, ...rest } = data.payload;
        displayHandle.current.addInput(sourceId, rest);
      }  else if (data.action === 'DISPLAY_REMOVE_INPUT') {
        const { sourceId } = data.payload;
        displayHandle.current.removeInput(sourceId);
      } else if (data.action === 'DISPLAY_CLEAR_INPUTS') {
        displayHandle.current.clearInputs();
      } else if (data.action === 'DISPLAY_RENDER') {
        displayHandle.current.render();
      }
    }

    ws.addEventListener('message', listener);

    return () => ws.removeEventListener('message', listener);
  }, [ws]);
    return <div className='fill' ref={container}/>;
}

export default Display1DComponent;
