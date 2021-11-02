import React, { useEffect } from 'react';
import './App.css';
import { useAppDispatch } from './app/hooks';
import DisplaysPanel from './components/displays-panel';
import PipelinesPanel from './components/pipelines-panel';
import OperatorsPanel from './components/operators-panel';
import StatusBar from './components/status-bar';
import { createSession } from './features/session';
import Split from 'react-split'

function App() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(createSession())
  }, [dispatch]);

  return (
    <div className="app">
      <div className="header">
      </div>
      <div className="content">
        <div className="inner-content">
          <OperatorsPanel/>
          <Split className="split">
            <PipelinesPanel/>
            <DisplaysPanel/>
          </Split>
        </div>
      </div>
      <div className="footer">
        <StatusBar/>
      </div>
    </div>
  );
}

export default App;
