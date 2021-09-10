import React, { useEffect, useRef, useState } from 'react';

import createEngine, {
  DefaultLinkModel,
  DefaultNodeModel,
  DiagramModel, DagreEngine, LinkModel, PortModel, DefaultPortModel
} from '@projectstorm/react-diagrams';

import {
  CanvasWidget
} from '@projectstorm/react-canvas-core';

import { NodeType, Pipeline } from '../types/pipeline';

type Props = {
  pipeline: Pipeline;
};

const inputPortId = (name: string) => `in://${name}`;
const outputPortId = (name: string) => `out://${name}`;

const PipelineComponent: React.FC<Props> = (props) => {

  const { pipeline } = props;

  const [iter, setIter] = useState(0);
  const engine = useRef(createEngine());
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

    const nodes: {[key: string]: DefaultNodeModel} = {};
    pipeline.nodes.forEach((node, i) => {
      let nodeModel: DefaultNodeModel;

      if (node.type === NodeType.Operator) {
        nodeModel = new DefaultNodeModel({
          name: `${node.id} - ${(node as any).image}`,
          color: 'rgb(0,192,255)',
        });
      } else if (node.type === NodeType.Display) {
        nodeModel = new DefaultNodeModel({
          name: `${node.id} - Display (${(node as any).display})`,
          color: 'rgb(255,192,0)',
        });
      } else {
        throw new Error('Unknown node type');
      }

      nodes[node.id] = nodeModel;
    });

    const links: LinkModel[] = [];
    pipeline.edges.forEach((edge) => {
      let sourcePort: PortModel | null = null;
      let targetPort: PortModel | null = null;

      if (nodes[edge.from.id]) {
        const node = nodes[edge.from.id];
        const portLabel = edge.from.port;
        const portId = outputPortId(edge.from.port);

        sourcePort = node.getPort(portId);
        if (!sourcePort) {
          const port = new DefaultPortModel({name: portId, label: portLabel, in: false});
          node.addPort(port);
          sourcePort = port;
        };
      }

      if (nodes[edge.to.id]) {
        const node = nodes[edge.to.id];
        const portLabel = edge.to.port;
        const portId = inputPortId(edge.to.port);

        targetPort = node.getPort(portId);
        if (!targetPort) {
          const port = new DefaultPortModel({name: portId, label: portLabel, in: true, maximumLinks: 1});
          node.addPort(port);
          targetPort = port;
        };
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
