import React from 'react';
import { useAppSelector } from '../app/hooks';

type Props = {};

const StatusBar: React.FC<Props> = () => {
  const currentSession = useAppSelector((state) => state.session.currentSession);
  const webSocketStatus = useAppSelector((state) => state.websocket.status);

  return (
    <div>
      <span>Session ID: {currentSession?.id}</span>
      <span> WS: {webSocketStatus}</span>
    </div>
  )
}

export default StatusBar;