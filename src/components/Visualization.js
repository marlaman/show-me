import React from 'react';
import ReactFlow from 'react-flow-renderer';

function Visualization({ elements }) {
  return <ReactFlow elements={elements} style={{ height: '500px' }} />;
}

export default Visualization;
