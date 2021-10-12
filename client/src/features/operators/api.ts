import { apiClient } from '../../client';
import { IdType } from '../../types';
import { Operator } from '../../types/operator';

export function fetchOperators(sessionId: IdType): Promise<Map<string, Operator>> {
  const url = 'operators';
  const params = {sessionId};

  const toMap = (json: any) => {
    const map = new Map<string, Operator>(Object.entries(json))
    return map;
  }

  return apiClient.get({url, params}).then(res => res.json()).then(payload => toMap(payload));
}


