import { useCallback } from 'react';
import { Handle, Position } from 'reactflow';

const handleStyle = { left: 10 };

function TextUpdaterNode({ data, isConnectable }) {
  const onChange = useCallback((evt) => {
    console.log(evt.target.value);
  }, []);

  return (
    <div className="text-updater-node" style={{ 
        width:'500px',      // Increased size by approximately 10x
        height: '150px', 
        
      }}>
      <Handle
        type="target"
        position={Position.Left}
        isConnectable={isConnectable}
      />
      <div style={{ 
        padding:'20px', 
        background: "#D6D5E6",  
        height: "100%"   // Increased size by approximately 10x
     
        
      }}>
        <label htmlFor="text"><b>Prompt:</b></label>
        <input id="text" name="text" onChange={onChange} className="nodrag" value = {data.label} style={{ 
        width:'90%',
           // Increased size by approximately 10x
        
      }}/>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        id="b"
        isConnectable={isConnectable}
      />
    </div>
  );
}

export default TextUpdaterNode;