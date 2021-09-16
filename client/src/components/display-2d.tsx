import React, { useEffect, useRef } from 'react';

import { useAppSelector } from '../app/hooks';
import { IdType } from '../types';
import { Display } from '../types/pipeline';

type Props = {
    display: Display;
}

class DisplayHandle2D {
  container: React.RefObject<HTMLImageElement>;
  sourceId?: IdType;
  scalars?: number[];
  shape?: [number, number];

  constructor(container: React.RefObject<HTMLImageElement>) {
    this.container = container;
    this.sourceId = undefined;
    this.scalars = undefined;
    this.shape = undefined;
  }

  addInput(sourceId: IdType, payload: any) {
    const { scalars, shape } = payload;
    this.sourceId = sourceId;
    this.scalars = scalars;
    this.shape = shape;
  }

  removeInput(sourceId: IdType) {
    if (this.sourceId === sourceId) {
      this.sourceId = undefined;
      this.scalars = undefined;
      this.shape = undefined;
    }
  }

  clearInputs() {
    this.sourceId = undefined;
    this.scalars = undefined;
    this.shape = undefined;
  }

  render() {
    if (this.scalars && this.shape && this.container.current) {
      const array = this.scalars;
      const shape = this.shape;
      const img = this.container.current;
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d')!;
      const [height, width] = shape;
      canvas.width = width;
      canvas.height = height;
      const imageData = new ImageData(width, height);
    //   const min = Math.min(...array)
    //   const max = Math.max(...array)
    //   const delta = max - min;

      array.forEach((val, idx) => {
        // const c = 255 * (val - min) / delta
        const c = val;
        imageData.data[idx * 4] = c;
        imageData.data[idx * 4 + 1] = c;
        imageData.data[idx * 4 + 2] = c;
        imageData.data[idx * 4 + 3] = 255;
      });

      context.putImageData(imageData, 0, 0);
      img.src = canvas.toDataURL();
    }
  }
}

const Display2DComponent: React.FC<Props> = (props) => {
  const ws = useAppSelector((state) => state.notifications.ws);

  const container = useRef<HTMLImageElement>(null);

  const displayHandle = useRef(new DisplayHandle2D(container));

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
    return <img style={{objectFit: 'contain', width: '100%'}} ref={container}/>;
}

export default Display2DComponent;
