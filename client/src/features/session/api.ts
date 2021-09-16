import { apiClient } from '../../client';
import { Session } from '../../types/session';

export function createSession(): Promise<Session> {
  const url = 'sessions';
  return apiClient.post({url}).then(res => res.json());
}
