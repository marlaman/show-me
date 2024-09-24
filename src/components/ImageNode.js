// ImageNode.js
import React from 'react';
import { Handle } from 'reactflow';  // Import Handle to allow connections

const ImageNode = ({ data }) => {
  return (
    <div 
      style={{ 
        width:'532px',      // Increased size by approximately 10x
        height: '700px', 
        border: '2px solid black', 
        borderRadius: '15px',  // More rounded edges
        textAlign: 'center',
        overflow: 'hidden',   // Prevent the image from overflowing
        backgroundColor: '#f9f9f9' // Optional: Add background for aesthetics
      }}
    >
      <img
        src={data.imageUrl}  // Image URL passed through the data prop
        alt="Node Image"
        style={{ 
          width: '100%', 
          height: '100%', 
          objectFit: 'contain' // Ensure the image fits within the node
        }}
      />
      {/* Enable target handle at the top */}
      <Handle type="target" position="left" style={{ background: '#555' }} />
      
      {/* Enable source handle at the bottom */}
      <Handle type="source" position="right" style={{ background: '#555' }} />
    </div>
  );
};

export default ImageNode;
