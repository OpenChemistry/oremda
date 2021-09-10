import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';

import { createSession as createSessionAPI } from './api';

import { Session } from '../../types/session';

import { connectNotifications } from '../notifications';

export type SessionState = {
  currentSession: Session | undefined;
}

const initialState: SessionState = {
  currentSession: undefined,
}

export const createSession = createAsyncThunk<Session>(
  'session/create',
  async (payload, thunkAPI) => {
    const session = await createSessionAPI();

    thunkAPI.dispatch(connectNotifications({sessionId: session.id}));
    return session;
  }
);

export const sessionSlice = createSlice({
  name: 'session',
  initialState,
  reducers: {
    setSession(state, action: PayloadAction<Session>) {
      state.currentSession = action.payload;
    },
  },
  // The `extraReducers` field lets the slice handle actions defined elsewhere,
  // including actions generated by createAsyncThunk or in other slices.
  extraReducers: (builder) => {
    builder
      .addCase(createSession.fulfilled, (state, action) => {
        state.currentSession = action.payload;
      })
  },
});

export const { setSession } = sessionSlice.actions;

export default sessionSlice.reducer;
