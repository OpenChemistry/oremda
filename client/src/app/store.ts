import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import sessionReducer from '../features/session';
import pipelinesReducer from '../features/pipelines';
import displaysReducer from '../features/displays';
import notificationsReducer from '../features/notifications';

export const store = configureStore({
  reducer: {
    session: sessionReducer,
    pipelines: pipelinesReducer,
    displays: displaysReducer,
    notifications: notificationsReducer,
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
