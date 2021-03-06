import { createAsyncThunk, createSlice, createEntityAdapter, PayloadAction } from '@reduxjs/toolkit';
import produce from 'immer';

import { RootState } from '../../app/store';
import {
  createPipeline as createPipelineAPI,
} from './api';

import { IdType } from '../../types';
import { Pipeline, PipelineEdge } from '../../types/pipeline';

export const pipelinesAdapter = createEntityAdapter<Pipeline>();

export type PipelineStatus = 'idle' | 'running' | 'error' | 'complete'

export interface PipelinesState extends ReturnType<typeof pipelinesAdapter['getInitialState']> {
  status: {[key: string]: PipelineStatus}
}

const initialState: PipelinesState = pipelinesAdapter.getInitialState({status: {}});

export const runPipeline = createAsyncThunk<Pipeline, {sessionId: IdType; pipeline: Pipeline}>(
  'pipelines/run',
  async (payload, thunkAPI) => {
    const { sessionId, pipeline } = payload;
    return await createPipelineAPI(sessionId, pipeline);
  }
)

export const pipelinesSlice = createSlice({
  name: 'pipelines',
  initialState,
  reducers: {
    setPipeline(state, action: PayloadAction<Pipeline>) {
      const pipeline = action.payload;
      pipelinesAdapter.setOne(state, pipeline);
      state.status[pipeline.id] = 'idle';
    },
    addEdge(state, action: PayloadAction<{pipelineId: IdType; edge: PipelineEdge}>) {
      const { pipelineId, edge } = action.payload;
      let pipeline = pipelinesAdapter.getSelectors().selectById(state, pipelineId);
      if (!pipeline) {
        return;
      }

      pipeline = produce(pipeline, (draft) => {
        draft.edges = draft.edges.filter(ed => ed.id !== edge.id);
        draft.edges.push(edge);
      });

      pipelinesAdapter.setOne(state, pipeline);
    },
    removeEdge(state, action: PayloadAction<{pipelineId: IdType; edgeId: IdType}>) {
      const { pipelineId, edgeId } = action.payload;
      let pipeline = pipelinesAdapter.getSelectors().selectById(state, pipelineId);
      if (!pipeline) {
        return;
      }

      pipeline = produce(pipeline, (draft) => {
        draft.edges = draft.edges.filter(ed => ed.id !== edgeId);
      });

      pipelinesAdapter.setOne(state, pipeline);
    },
  },
  // The `extraReducers` field lets the slice handle actions defined elsewhere,
  // including actions generated by createAsyncThunk or in other slices.
  extraReducers: (builder) => {
  },
});

export const pipelinesSelector = pipelinesAdapter.getSelectors<RootState>(state => state.pipelines);

export const { setPipeline, addEdge, removeEdge } = pipelinesSlice.actions;

export default pipelinesSlice.reducer;
