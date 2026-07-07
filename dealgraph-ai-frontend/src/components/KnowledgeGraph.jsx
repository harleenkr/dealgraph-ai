import React, { useState, useEffect, useMemo } from 'react';
import { ReactFlow, ReactFlowProvider, useReactFlow, Background, Controls, MarkerType, useNodesState, useEdgesState, Handle, Position } from '@xyflow/react';
import dagre from 'dagre';

const colorMap = {
  'Low': '#10b981',
  'Medium': '#f59e0b',
  'High': '#ef4444',
  'Critical': '#b91c1c'
};

const typeStyles = {
  Customer: { bg: 'rgba(59, 130, 246, 0.1)', icon: '🏢' },
  Deal: { bg: 'rgba(139, 92, 246, 0.1)', icon: '💼' },
  Risk: { bg: 'rgba(239, 68, 68, 0.1)', icon: '⚠️' },
  Owner: { bg: 'rgba(245, 158, 11, 0.1)', icon: '👤' },
  Process: { bg: 'rgba(245, 158, 11, 0.1)', icon: '👤' },
  Violation: { bg: 'rgba(239, 68, 68, 0.15)', icon: '🚫' },
  Recommendation: { bg: 'rgba(16, 185, 129, 0.1)', icon: '✅' },
  Metric: { bg: 'rgba(255, 255, 255, 0.05)', icon: '📊' },
  Condition: { bg: 'rgba(255, 255, 255, 0.05)', icon: '⚙️' },
  default: { bg: 'var(--bg-panel)', icon: '📌' }
};

const CustomNode = ({ data }) => {
  const riskBorderColor = colorMap[data.riskLevel] || 'var(--border-color)';
  const styleConf = typeStyles[data.type] || typeStyles.default;
  
  const animationStyle = data.isProcessing ? 'pulse-border 1.5s infinite' : 'none';
  
  return (
    <div style={{
      background: styleConf.bg,
      border: `2px solid ${data.isProcessing ? '#ffffff' : riskBorderColor}`,
      borderRadius: '24px', 
      padding: '12px 20px',
      color: 'white',
      width: '280px', // Increased node width
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      boxShadow: data.isProcessing ? `0 0 15px ${riskBorderColor}` : `0 0 5px ${riskBorderColor}40`,
      fontSize: '0.9rem',
      animation: animationStyle,
      transition: 'all 0.3s ease',
      wordWrap: 'break-word',
      position: 'relative'
    }}>
      <Handle type="target" position={Position.Top} style={{ visibility: 'hidden' }} />
      <div style={{ fontSize: '1.6rem' }}>{styleConf.icon}</div>
      <div style={{ textAlign: 'left', flex: 1 }}>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '2px', fontWeight: 600 }}>
          {data.type}
        </div>
        <div style={{ fontWeight: 600, fontSize: '0.9rem', lineHeight: '1.3' }}>{data.label}</div>
      </div>
      <Handle type="source" position={Position.Bottom} style={{ visibility: 'hidden' }} />
    </div>
  );
};

const nodeTypes = { custom: CustomNode };

const getLayoutedElements = (nodes, edges, direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  
  // Increased node dimensions but packed horizontally tighter
  const nodeWidth = 300; 
  const nodeHeight = 80; 
  
  // Pack nodes closely together horizontally (nodesep: 15) to prevent massive zooming
  dagreGraph.setGraph({ rankdir: direction, ranksep: 160, nodesep: 15 });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const newNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return { 
      ...node, 
      position: { 
        x: nodeWithPosition.x - nodeWidth / 2, 
        y: nodeWithPosition.y - nodeHeight / 2 
      } 
    };
  });

  return { nodes: newNodes, edges };
};

function KnowledgeGraphInner({ graphData }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const { fitView } = useReactFlow();
  
  const layoutedGraph = useMemo(() => {
    if (!graphData || !graphData.nodes) return { nodes: [], edges: [] };
    
    const initialNodes = graphData.nodes.map((n) => ({
      id: n.id,
      type: 'custom',
      position: { x: 0, y: 0 },
      data: { label: n.label, type: n.type, riskLevel: n.riskLevel, isProcessing: false }
    }));

    const initialEdges = graphData.edges.map((e, i) => ({
      id: `e-${i}`,
      source: e.source,
      target: e.target,
      label: e.label,
      animated: true,
      style: { stroke: 'var(--accent-blue)', opacity: 0.7, strokeWidth: 2 },
      labelStyle: { fill: 'var(--text-primary)', fontSize: 11, fontWeight: 600 },
      labelBgStyle: { fill: 'var(--bg-panel)', opacity: 0.9 },
      markerEnd: { type: MarkerType.ArrowClosed, color: 'var(--accent-blue)' }
    }));

    return getLayoutedElements(initialNodes, initialEdges, 'TB');
  }, [graphData]);

  useEffect(() => {
    if (layoutedGraph.nodes.length === 0) {
      setNodes([]);
      setEdges([]);
      return;
    }

    setNodes([]);
    setEdges([]);
    
    let currentIndex = 0;
    const totalNodes = layoutedGraph.nodes.length;
    
    const interval = setInterval(() => {
      if (currentIndex >= totalNodes) {
        clearInterval(interval);
        setNodes(prev => prev.map(n => ({...n, data: {...n.data, isProcessing: false}})));
        setTimeout(() => fitView({ padding: 0.2, duration: 800 }), 100);
        return;
      }
      
      const nodeToAdd = layoutedGraph.nodes[currentIndex];
      
      setNodes((prevNodes) => {
        const settledNodes = prevNodes.map(n => ({...n, data: {...n.data, isProcessing: false}}));
        return [...settledNodes, { ...nodeToAdd, data: { ...nodeToAdd.data, isProcessing: true } }];
      });
      
      setEdges(() => {
        const visibleNodeIds = new Set(layoutedGraph.nodes.slice(0, currentIndex + 1).map(n => n.id));
        return layoutedGraph.edges.filter(e => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target));
      });
      
      currentIndex++;
      
      // Auto-zoom and pan to fit the newly added nodes nicely
      setTimeout(() => {
        fitView({ padding: 0.2, duration: 400 });
      }, 50);

    }, 800); // Slower interval (800ms) to let the user track the flow clearly
    
    return () => clearInterval(interval);
  }, [layoutedGraph, setNodes, setEdges, fitView]);

  return (
    <ReactFlow 
      nodes={nodes} 
      edges={edges} 
      nodeTypes={nodeTypes} 
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      fitView
      fitViewOptions={{ padding: 0.1 }}
      nodesDraggable={true}
      minZoom={0.3}
      maxZoom={2}
    >
      <Background color="rgba(255,255,255,0.05)" />
      <Controls />
    </ReactFlow>
  );
}

export default function KnowledgeGraph({ graphData }) {
  if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
    return (
      <div className="glass-panel full-width" style={{ height: '750px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        Knowledge graph will appear here after analysis.
      </div>
    );
  }

  return (
    <div id="knowledge-graph-container" className="glass-panel full-width" style={{ height: '750px', padding: 0, overflow: 'hidden', position: 'relative' }}>
      <div style={{ position: 'absolute', zIndex: 10, padding: '1.5rem', background: 'linear-gradient(to bottom, var(--bg-panel) 0%, transparent 100%)', width: '100%', pointerEvents: 'none' }}>
        <h2 style={{ margin: 0 }}>Live Knowledge Graph</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Real-time agentic workflow mapping</p>
      </div>
      <ReactFlowProvider>
        <KnowledgeGraphInner graphData={graphData} />
      </ReactFlowProvider>
    </div>
  );
}
