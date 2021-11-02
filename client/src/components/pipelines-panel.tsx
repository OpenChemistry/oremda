import React  from 'react';

import { v4 as uuidv4 } from 'uuid';

import { useAppDispatch, useAppSelector } from '../app/hooks';
import { setDisplay } from '../features/displays';
import { pipelinesSelector, setPipeline } from '../features/pipelines';
import { createPipeline } from '../features/pipelines/api';
import { Pipeline, NodeType, isDisplayNode } from '../types/pipeline';
import PipelineComponent from './pipeline';

import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Stack from '@mui/material/Stack';

type Props = {};

const PipelinesPanel: React.FC<Props> = () => {
  const dispatch = useAppDispatch();
  const pipelines = useAppSelector(pipelinesSelector.selectAll);
  const pipelinesStatus = useAppSelector((state) => state.pipelines.status);
  const currentSession = useAppSelector((state) => state.session.currentSession);
  const operators = useAppSelector((state) => state.operators.operators);

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
    const pipeline: Pipeline = {
      id: uuidv4(),
      nodes: [],
      edges: [],
    }
    dispatch(setPipeline(pipeline));
  }

  const runPipeline = (pipeline: Pipeline) => {
    if (!currentSession) {
      return;
    }

    createPipeline(currentSession.id, pipeline);
  }

  const [anchorEl, setAnchorEl] = React.useState(null);

  const open = Boolean(anchorEl);

  const handleClick = (event: any) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement> ) => {
    const { pipeline } = event.currentTarget.dataset;

    if (pipeline !== undefined) {
      addPipeline(pipeline);
    }

    setAnchorEl(null);
  };

  const handleClose = () => {
    setAnchorEl(null);
  }

  return (
    <div className="pipelines-panel">
        <Stack spacing={1} direction="row">
          <Button variant="contained" onClick={() => newPipeline()} size='small'>New Pipeline</Button>
          <Button
            id="basic-button"
            aria-controls="basic-menu"
            aria-haspopup="true"
            aria-expanded={open ? 'true' : undefined}
            onClick={handleClick}
            variant="contained"
            size="small"
          >
            Load Existing Pipeline
          </Button>
          <Menu
            id="basic-menu"
            anchorEl={anchorEl}
            open={open}
            onClose={handleClose}
            MenuListProps={{
              'aria-labelledby': 'basic-button',
            }}
          >
            <MenuItem data-pipeline='pipeline_1d.json' onClick={handleMenuClick}>Background Subtraction</MenuItem>
            <MenuItem data-pipeline='pipeline_2d.json' onClick={handleMenuClick}>Gaussian Blur</MenuItem>
            <MenuItem data-pipeline='pipeline_peak.json' onClick={handleMenuClick}>Peak Fitting</MenuItem>
            <MenuItem onClick={handleMenuClick}>Nano particle Orientation</MenuItem>
            <MenuItem onClick={handleMenuClick}>Bragg Disc Detection</MenuItem>

          </Menu>
      </Stack>

      {
        pipelines.map(pipeline => {
          return (
            <React.Fragment key={pipeline.id}>
              <p><span>Pipeline</span> {pipeline.id.slice(-8)} <Button variant="contained"  color="success" onClick={() => runPipeline(pipeline)} size="small">run</Button></p>
              <div className="pipeline-container">
                <PipelineComponent pipeline={pipeline} operators={operators}/>
              </div>
            </React.Fragment>
          );
        })
      }
    </div>
  )
}

export default PipelinesPanel;
