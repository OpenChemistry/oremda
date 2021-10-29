import React, { useEffect, useRef, useState } from 'react';

import createEngine, {
  DefaultLinkModel,
  DiagramModel, DagreEngine, LinkModel,
} from '@projectstorm/react-diagrams';

import { OremdaNodeModel, OremdaPortModel } from './models';
import { OremdaNodeFactory } from './factories';

import {
  CanvasWidget
} from '@projectstorm/react-canvas-core';

import { NodeType, Pipeline } from '../../types/pipeline';

type Props = {
  pipeline: Pipeline;
};

function createCustomEngine() {
  const engine = createEngine();

  engine.getNodeFactories().registerFactory(new OremdaNodeFactory());

  return engine;
}

const PipelineComponent: React.FC<Props> = (props) => {

  const { pipeline } = props;

  const [iter, setIter] = useState(0);
  const engine = useRef(createCustomEngine());
  const dagre = useRef(new DagreEngine({
    graph: {
      rankdir: 'LR',
      align: 'UL',
      ranker: 'longest-path',
      nodesep: 100,
      ranksep: 50,
      edgesep: 10,
      marginx: 25,
      marginy: 25,
    },
    // includeLinks: true,
  }));

  // Update the pipeline graph when the pipeline prop changes
  useEffect(() => {
    if (!engine.current || !dagre.current) {
      return;
    }

    const nodes: {[key: string]: OremdaNodeModel} = {};
    pipeline.nodes.forEach((node, i) => {
      let nodeModel = new OremdaNodeModel(node);
      nodes[node.id] = nodeModel;
    });

    const links: LinkModel[] = [];
    pipeline.edges.forEach((edge) => {
      let sourcePort: OremdaPortModel | null = null;
      let targetPort: OremdaPortModel | null = null;

      if (nodes[edge.from.id]) {
        const node = nodes[edge.from.id];
        const portLabel = edge.from.port;
        const portType = edge.type;

        sourcePort = node.getOutPort(portLabel);
        if (!sourcePort) {
          sourcePort = node.addOutPort(portLabel, portType);
        }
      }

      if (nodes[edge.to.id]) {
        const node = nodes[edge.to.id];
        const portLabel = edge.to.port;
        const portType = edge.type;

        targetPort = node.getInPort(portLabel);
        if (!targetPort) {
          targetPort = node.addInPort(portLabel, portType);
        }
      }

      if (sourcePort && targetPort) {
        const link = new DefaultLinkModel();
        link.setSourcePort(sourcePort);
        link.setTargetPort(targetPort);
        links.push(link);
      }
    });

    const model = new DiagramModel();
    model.addAll(...Object.values(nodes), ...links);
    engine.current.setModel(model);

    setIter(iter + 1);

    setTimeout(() => {
      dagre.current.redistribute(model);
      engine.current.repaintCanvas();
    }, 0);
  }, [pipeline]);

  if (!engine.current || !engine.current.getModel()) {
    return null;
  }

  return <CanvasWidget className='pipeline-diagram' engine={engine.current} />;
}

export default PipelineComponent;
