import React, { useState }  from 'react';

import { v4 as uuidv4 } from 'uuid';

import { useAppDispatch, useAppSelector } from '../app/hooks';
import { setDisplay } from '../features/displays';
import { pipelinesSelector, setPipeline } from '../features/pipelines';
import { createPipeline } from '../features/pipelines/api';
import { Pipeline, NodeType, isDisplayNode } from '../types/pipeline';
import PipelineComponent from './pipeline-graph';
import { NewPipelineWidget } from './new-pipeline'

type Props = {};

const PipelinesPanel: React.FC<Props> = () => {
  const dispatch = useAppDispatch();
  const pipelines = useAppSelector(pipelinesSelector.selectAll);
  const pipelinesStatus = useAppSelector((state) => state.pipelines.status);
  const currentSession = useAppSelector((state) => state.session.currentSession);
  const operators = useAppSelector((state) => state.operators.operators);
  const [showNewPipeline, setShowNewPipeline] = useState(false);

  const addPipeline = (url: string) => {
    fetch(url)
      .then(res => res.json())
      .then((pipeline: Pipeline) => {
        pipeline.id = pipeline.id || uuidv4();
        pipeline.nodes = pipeline.nodes.map(node => ({...node, type: node.type || NodeType.Operator}));
        dispatch(setPipeline(pipeline));
        pipeline.nodes.filter(isDisplayNode).forEach(displayNode => {
          dispatch(setDisplay({id: displayNode.id, type: displayNode.display}));
        });
      });
  }

  // We should rework this so we add multiple new pipelines ...
  const newPipeline = () => {
    setShowNewPipeline(true);
  }

  const runPipeline = (pipeline: Pipeline) => {
    if (!currentSession) {
      return;
    }

    createPipeline(currentSession.id, pipeline);
  }

  return (
    <div className="pipelines-panel">
      <h4>
        Pipelines
        <button onClick={() => newPipeline()}>New Pipeline</button>
        <button onClick={() => addPipeline('pipeline_1d.json')}>Add 1D</button>
        <button onClick={() => addPipeline('pipeline_2d.json')}>Add 2D</button>
        <button onClick={() => addPipeline('pipeline_peak.json')}>Add Peak</button>
      </h4>


      {
        pipelines.map(pipeline => {
          return (
            <React.Fragment key={pipeline.id}>
              <p><span>Pipeline</span> {pipeline.id.slice(-8)} <button onClick={() => runPipeline(pipeline)}>run</button></p>
              <div className="pipeline-container">
                <PipelineComponent pipeline={pipeline}/>
              </div>
            </React.Fragment>
          );
        })
      }
      { showNewPipeline &&
      <div>
        <NewPipelineWidget operators={ operators }/>
      </div>
      }
    </div>
  )
}

export default PipelinesPanel;
