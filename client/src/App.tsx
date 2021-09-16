import React, { useEffect, useState } from 'react';
import './App.css';
import { useAppDispatch } from './app/hooks';
import DisplaysPanel from './components/displays-panel';
import PipelineComponent from './components/pipeline-graph';
import PipelinesPanel from './components/pipelines-panel';
import StatusBar from './components/status-bar';
import { createSession } from './features/session';
import { NodeType, Pipeline } from './types/pipeline';

function App() {
  const [pipeline, setPipeline] = useState<Pipeline>();
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(createSession())
  }, [dispatch]);

  useEffect(() => {
    function fetchPipeline(url: string) {
      fetch(url)
        .then(res => res.json())
        .then((pipeline: Pipeline) => {
          pipeline.nodes = pipeline.nodes.map(node => ({...node, type: node.type || NodeType.Operator}));
          setPipeline(pipeline);
        });
    }

    fetchPipeline('pipeline_1d.json');

    setTimeout(() => {
      fetchPipeline('pipeline_2d.json');
    }, 5000)
  }, []);

  if (!pipeline) {
    return null;
  }

  return (
    <div className="app">
      <div className="header">
      </div>
      <div className="content">
        <div className="inner-content">
          <PipelinesPanel/>
          <DisplaysPanel/>
        </div>
      </div>
      <div className="footer">
        <StatusBar/>
      </div>
    </div>
  );
}

export default App;
