import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import sessionReducer from '../features/session';
import pipelinesReducer from '../features/pipelines';
import displaysReducer from '../features/displays';
import webSocketReducer from '../features/websocket';

export const store = configureStore({
  reducer: {
    session: sessionReducer,
    pipelines: pipelinesReducer,
    displays: displaysReducer,
    websocket: webSocketReducer,
  },
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
