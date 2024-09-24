import React, { useCallback } from 'react';
import { Handle, Position } from 'reactflow';

function CodeAnswerNode({ data, isConnectable }) {
  const onScroll = useCallback((evt) => {
    evt.stopPropagation();
  }, []);

  return (
    <div style={{
      width: '400px',
      border: '1px solid #ccc',
      borderRadius: '8px',
      background: "#D3D3D3",
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
    }}>
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      <div style={{ 
        padding: '10px', 
        borderBottom: '1px solid #ccc',
        fontWeight: 'bold',
        fontFamily: ''
      }}>
        Python Interpreter Answer:
      </div>
      <div 
        style={{ 
          flex: 1,
          padding: '10px',
          overflowY: 'auto',
          background: "white",
        }}
        onScroll={onScroll}
      >
        <div style={{
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}>
          {data.label}
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        id="b"
        isConnectable={isConnectable}
      />
    </div>
  );
}

export default CodeAnswerNode;