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

      if (ev.payload.displayId !== props.display.id) {
        return;
      }

      const blob = new Blob([ev.payload.imageSrc], { type: 'image/png' });
      const url = URL.createObjectURL(blob);
      displayHandle.current.render(url);
    }

    notifications.addNotificationEventListener('DISPLAY_RENDER', listener);

    return () => notifications.removeNotificationEventListener('message', listener);
  }, [notifications]);

  const style = {
    objectFit: 'contain',
    width: '100%',
    top: '50%',
    left: '50%',
    position: 'absolute',
    transform: 'translate(-50%,-50%)',
    maxHeight: '100%',
  } as any;

  return <img style={style} ref={container}/>;
}

export default DisplayRemoteComponent;
