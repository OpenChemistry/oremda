import React from 'react';
import { useAppSelector } from '../app/hooks';

type Props = {};

const StatusBar: React.FC<Props> = () => {
  const currentSession = useAppSelector((state) => state.session.currentSession);
  const notificationStatus = useAppSelector((state) => state.notifications.status);

  return (
    <div>
      <span>Session ID: {currentSession?.id}</span>
      <span> WS: {notificationStatus}</span>
    </div>
  )
}

export default StatusBar;
