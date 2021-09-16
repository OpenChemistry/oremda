import { apiClient } from '../../client';
import { IdType } from '../../types';
import { Pipeline } from '../../types/pipeline';

export function createPipeline(sessionId: IdType, pipeline: Pipeline): Promise<Pipeline> {
  const url = 'pipelines';
  const params = {sessionId};
  return apiClient.post({url, params, json: pipeline}).then(res => res.json()).then(payload => payload.graph);
}
