import React, { useEffect, useRef } from 'react';

import { Display } from '../types/pipeline';
import { useNotifications, NotificationEvent} from '../notifications';



type Props = {
    display: Display;
}

class RemoteDisplayHandle {
  container: React.RefObject<HTMLImageElement>;

  constructor(container: React.RefObject<HTMLImageElement>) {
    this.container = container;
  }

  render(src: string) {
    if (this.container.current) {
        this.container.current.src = src;
    }
  }
}

const DisplayRemoteComponent: React.FC<Props> = (props) => {
  const container = useRef<HTMLImageElement>(null);

  const displayHandle = useRef(new RemoteDisplayHandle(container));

  const notifications = useNotifications();

  useEffect(() => {
    if (notifications === undefined) {
      return;
    }

    const listener = (ev: NotificationEvent) => {
      if (!displayHandle.current) {
        return;
      }

      const data = ev.data;

      if (data.type !== '@@OREMDA') {
        return;
      }

      if (data.payload.displayId !== props.display.id) {
        return;
      }

      if (data.action === 'DISPLAY_RENDER') {
        const blob = new Blob([data.payload.imageSrc], { type: 'image/png' });
        const url = URL.createObjectURL(blob);
        displayHandle.current.render(url);
      }
    }

    notifications.addNotificationEventListener('message', listener);

    return () => notifications.removeNotificationEventListener('message', listener);
  }, [notifications]);
    return <img style={{objectFit: 'contain', width: '100%'}} ref={container}/>;
}

export default DisplayRemoteComponent;
