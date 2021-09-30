import React, { useEffect, useRef } from 'react';

import { useAppSelector } from '../app/hooks';
import { Display } from '../types/pipeline';

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
  const ws = useAppSelector((state) => state.notifications.ws);

  const container = useRef<HTMLImageElement>(null);

  const displayHandle = useRef(new RemoteDisplayHandle(container));

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

      if (data.action === 'DISPLAY_RENDER') {
        displayHandle.current.render(data.payload.imageSrc);
      }
    }

    ws.addEventListener('message', listener);

    return () => ws.removeEventListener('message', listener);
  }, [ws]);
    return <img style={{objectFit: 'contain', width: '100%'}} ref={container}/>;
}

export default DisplayRemoteComponent;
