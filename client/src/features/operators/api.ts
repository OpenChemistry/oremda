import { apiClient } from '../../client';
import { IdType } from '../../types';
import { OperatorDefinition } from '../../types/operator';

export function fetchOperators(sessionId: IdType): Promise<{[key: string]: OperatorDefinition}> {
  const url = 'operators';
  const params = {sessionId};

  const toMap = (json: any) => {
    const map = new Map<string, OperatorDefinition>(Object.entries(json))
    return map;
  }

  return apiClient.get({url, params}).then(res => res.json());
}


