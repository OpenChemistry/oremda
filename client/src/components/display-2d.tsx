import React, { useEffect, useRef } from 'react';

import { useAppSelector } from '../app/hooks';
import { IdType } from '../types';
import { Display } from '../types/pipeline';
import { useNotifications, NotificationEvent } from '../notifications';

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
  const container = useRef<HTMLImageElement>(null);

  const displayHandle = useRef(new DisplayHandle2D(container));

  const notifications = useNotifications();

  useEffect(() => {

    if (notifications === undefined) {
      return;
    }

    const validDisplayHandle =  (): boolean => {
      return displayHandle.current !== undefined;
    }

    const matchingDisplay = (ev: NotificationEvent): boolean => {
      return ev.payload.displayId === props.display.id;
    }

    const addInputListener = (ev: NotificationEvent) => {
      if (!validDisplayHandle() || !matchingDisplay(ev)) {
        return;
      }

      const { sourceId, ...rest } = ev.payload;
      displayHandle.current.addInput(sourceId, rest);
    }

    const removeInputListener = (ev: NotificationEvent) => {
      if (!validDisplayHandle() || !matchingDisplay(ev)) {
        return;
      }

      const { sourceId } = ev.payload;
      displayHandle.current.removeInput(sourceId);
    }

    const clearInputsListener = (ev: NotificationEvent) => {
      if (!validDisplayHandle() || !matchingDisplay(ev)) {
        return;
      }
      displayHandle.current.clearInputs();
    }

    const renderListener = (ev: NotificationEvent) => {
      if (!validDisplayHandle() || !matchingDisplay(ev)) {
        return;
      }

      displayHandle.current.render();
    }

    notifications.addNotificationEventListener('DISPLAY_ADD_INPUT', addInputListener);
    notifications.addNotificationEventListener('DISPLAY_REMOVE_INPUT', removeInputListener);
    notifications.addNotificationEventListener('DISPLAY_CLEAR_INPUTS', clearInputsListener);
    notifications.addNotificationEventListener('DISPLAY_RENDER', renderListener);

    return () => {
      notifications.removeNotificationEventListener('DISPLAY_ADD_INPUT', addInputListener);
      notifications.removeNotificationEventListener('DISPLAY_REMOVE_INPUT', removeInputListener);
      notifications.removeNotificationEventListener('DISPLAY_CLEAR_INPUTS', clearInputsListener);
      notifications.removeNotificationEventListener('DISPLAY_RENDER', renderListener);
    }
  }, [notifications]);
    return <img style={{objectFit: 'contain', width: '100%'}} ref={container}/>;
}

export default Display2DComponent;
