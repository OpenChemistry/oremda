import React, { useEffect, useRef } from 'react';

import Plotly from 'plotly.js';

import { useAppSelector } from '../app/hooks';
import { IdType } from '../types';
import { Display } from '../types/pipeline';
import { useNotifications, NotificationEvent } from '../notifications';

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
  const container = useRef<HTMLDivElement>(null);

  const displayHandle = useRef(new DisplayHandle1D(container));

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
    return <div className='fill' ref={container}/>;
}

export default Display1DComponent;
