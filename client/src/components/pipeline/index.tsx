import React, { useEffect, useRef, useState } from 'react';

import createEngine, {
  DefaultLinkModel,
  DiagramModel, DagreEngine, LinkModel,
  DiagramListener, LinkModelGenerics,
  LinkModelListener,
} from '@projectstorm/react-diagrams';


import { v4 as uuidv4 } from 'uuid';
import produce from 'immer';

import { OremdaNodeModel, OremdaPortModel } from './models';
import { OremdaNodeFactory } from './factories';

import {
  CanvasWidget
} from '@projectstorm/react-canvas-core';

import { DisplayNode, DisplayType, NodeType, OperatorNode, Pipeline, PipelineEdge } from '../../types/pipeline';
import { OperatorDefinition } from '../../types/operator'
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { setPipeline, addEdge, removeEdge } from '../../features/pipelines';
import { setDisplay } from '../../features/displays';

type Props = {
  pipeline: Pipeline;
  operators: {[key: string]: OperatorDefinition} | undefined
};

function createCustomEngine() {
  const engine = createEngine();

  engine.getNodeFactories().registerFactory(new OremdaNodeFactory());

  return engine;
}

const PipelineComponent: React.FC<Props> = (props) => {

  const { pipeline, operators } = props;

  const dispatch = useAppDispatch();
  const [iter, setIter] = useState(0);
  const engine = useRef(createCustomEngine());
  const firstDraw = useRef(true);
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

    let currentModel = engine.current.getModel();
    if (currentModel) {
      // currentModel.clearListeners();
      // currentModel.getLinks().forEach(link => {
      //   link.clearListeners();
      // });
    } else {
      currentModel = new DiagramModel();
    }

    const currentNodes = currentModel.getNodes();

    const nodes: {[key: string]: OremdaNodeModel} = {};
    pipeline.nodes.forEach((node, i) => {
      let definition: OperatorDefinition | undefined;
      if (node.type === NodeType.Operator && operators) {
        const operatorNode = node as OperatorNode;
        definition = operators[operatorNode.image];
      }
      let nodeModel = new OremdaNodeModel(node, definition);
      for (let currentNode of currentNodes) {
        if (currentNode.getID() === nodeModel.getID()) {
          nodeModel.setPosition(currentNode.getPosition());
          break;
        }
      }
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

    const model = currentModel;
    // Clear out previous nodes/links
    model.getNodes().forEach(node => model.removeNode(node));
    model.getLinks().forEach(link => model.removeLink(link));
    model.addAll(...Object.values(nodes), ...links);

    engine.current.setModel(model);

    const linkListeners: [LinkModel<LinkModelGenerics>, LinkModelListener][] = [];

    const updatePipelineEdges = (link: LinkModel<LinkModelGenerics>, action: 'create'|'update'|'delete') => {
      const sourcePort: OremdaPortModel = link.getSourcePort() as any;
      const targetPort: OremdaPortModel = link.getTargetPort() as any;

      if (!sourcePort || !targetPort) {
        return;
      }

      const sourceOptions = sourcePort.getOptions();
      const sourceParent = sourcePort.getParent();

      const targetOptions = targetPort.getOptions();
      const targetParent = targetPort.getParent();

      if (action === 'delete') {
        dispatch(removeEdge({pipelineId: pipeline.id, edgeId: link.getID()}));
        return;
      }

      if (action === 'update') {
        if (sourceOptions.portType !== targetOptions.portType) {
          dispatch(removeEdge({pipelineId: pipeline.id, edgeId: link.getID()}));
          return;
        }

        const edge: PipelineEdge = {
          id: link.getID(),
          type: sourceOptions.portType,
          from: {
            id: sourceParent.getID(),
            port: sourceOptions.label,
          },
          to: {
            id: targetParent.getID(),
            port: targetOptions.label,
          }
        }

        dispatch(addEdge({pipelineId: pipeline.id, edge}));
      }
    }

    const linkListener: LinkModelListener = {
      deregister() {},
      entityRemoved(ev: any) {
        const link: LinkModel<LinkModelGenerics> = ev.entity as any;
        updatePipelineEdges(link, 'delete');
      },
      sourcePortChanged(ev: any) {
        const link: LinkModel<LinkModelGenerics> = ev.entity;
        updatePipelineEdges(link, 'update');
      },
      targetPortChanged(ev: any) {
        const link: LinkModel<LinkModelGenerics> = ev.entity;
        updatePipelineEdges(link, 'update');
      }
    }

    const modelListener: DiagramListener = {
      deregister() {},
      linksUpdated(ev:any) {
        const isCreated: boolean = ev.isCreated;
        const link: LinkModel<LinkModelGenerics> = ev.link;

        if (isCreated) {

          updatePipelineEdges(link, 'create');

          link.registerListener(linkListener);

          linkListeners.push([link, linkListener]);
        }
      }
    }
    currentModel.registerListener(modelListener)

    setIter(iter + 1);

    const redistribute = firstDraw.current;

    setTimeout(() => {
      if (redistribute) {
        firstDraw.current = false;
        dagre.current.redistribute(model);
        engine.current.repaintCanvas();
      }
    }, 0);

    return () => {
      currentModel.clearListeners();
      currentModel.getLinks().forEach(link => {
        link.clearListeners();
      });
    }
  }, [pipeline, operators]);

  if (!engine.current || !engine.current.getModel()) {
    return null;
  }

  return (
    <div style={{width: '100%', height: '100%'}}
      onDrop={(event) => {
        if (event.dataTransfer.getData('operator-node')) {
          var opData = JSON.parse(event.dataTransfer.getData('operator-node'));
          const imageName: string = opData.imageName;
          const operator: OperatorDefinition = opData.operator;

          const operatorNode: OperatorNode = {
            id: uuidv4(),
            image: imageName,
            params: Object.entries(operator.params).reduce((params, [paramKey, paramDesc]) => {
              params[paramKey] = (paramDesc as any).default;
              return params;
            }, {} as any),
            type: NodeType.Operator
          }

          // TODO: Remove these hardcoded parameter values
          if (imageName.startsWith('oremda/tiff_reader')) {
            operatorNode.params['filename'] = 'passport.tiff';
          }

          if (imageName.startsWith('oremda/gaussian_blur')) {
            operatorNode.params['sigma'] = 10;
          }

          if (imageName.startsWith('oremda/crop2d')) {
            operatorNode.params['bounds'] = [0, 300, 0, 300];
          }

          //

          const nextPipeline = produce(pipeline, draft => {
            draft.nodes.push(operatorNode);
          });
          dispatch(setPipeline(nextPipeline));
        } else if (event.dataTransfer.getData('display-node')) {
          var opData = JSON.parse(event.dataTransfer.getData('display-node'));
          const displayType: DisplayType = opData.displayType;

          const displayNode: DisplayNode = {
            id: uuidv4(),
            type: NodeType.Display,
            display: displayType,
            params: {},
          }

          const nextPipeline = produce(pipeline, draft => {
            draft.nodes.push(displayNode);
          });
          dispatch(setPipeline(nextPipeline));
          dispatch(setDisplay({id: displayNode.id, type: displayNode.display}))
        }
      }}
      onDragOver={(event) => {
        event.preventDefault();
      }}
    >
      <CanvasWidget className='pipeline-diagram' engine={engine.current} />
    </div>
  );
}

export default PipelineComponent;
