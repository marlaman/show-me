import React, { useEffect, useReducer, useState, memo, useRef } from 'react';
import ReactFlow, { ReactFlowProvider, Controls, Background, applyNodeChanges, applyEdgeChanges, ConnectionLineType,Handle, Position, useReactFlow, useNodesInitialized } from 'reactflow';

import 'reactflow/dist/style.css';
import io from 'socket.io-client';
import dagre from 'dagre';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { Typography, Paper, Box, Button, TextField } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import './index.css';
import ImageNode from './components/ImageNode';
import DevTools from './Devtools';
import TextUpdaterNode from './components/TextUpdaterNode.js';
import DisplayNode from './components/DisplayNode.js';
import CodeAnswerNode from './components/CodeAnswerNode.js';
import { ClipboardList, ListTodo, TestTube2 } from 'lucide-react'
import './components/text-updater-node.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import SoftwareFlowWithProvider from './SoftwareAgent.js';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import CopyButton from './components/CopyButton.js';

const socket = io('http://localhost:5088');

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));
dagreGraph.setGraph({ rankdir: 'TB', ranksep: 20 });
const nodeWidth = 400;
const nodeHeight = 300;



const MainTaskNode = ({ data }) => {
  return (
    <div className="bg-primary text-primary-foreground rounded-lg shadow-lg p-6 border-2 border-primary w-80" style={{ backgroundColor: "#D6D5E6", position: 'relative' }}>
      <Handle type="target" position={Position.Top} className="w-3 h-3" />

      {/* Test Icon + Tests Passed/Total in Orange Rounded Rectangle */}
      {data.hasTests && <div style={{
        position: 'absolute', 
        top: '10px', 
        right: '10px',  // Adjusted to top-right corner
        backgroundColor: '#FFA500',  // Orange color
        borderRadius: '12px', 
        padding: '4px 8px', 
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white'
      }}>
        <TestTube2 className="w-5 h-5 mr-1" />
        <span style={{ fontSize: '0.875rem' }}>{data.passedTests}/{data.totalTests}</span>
      </div>}

      <div className="flex items-center mb-4">
        <ClipboardList className="w-8 h-8 mr-3" />
        <h2 className="text-2xl font-bold">Main Task</h2>
      </div>
      
      <p className="text-lg font-medium mb-4">
        {data.label}
      </p>

      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
    </div>
  );
};

const SubTaskNode = ({ data }) => {
  return (
    <div className="bg-secondary text-secondary-foreground rounded-lg shadow-md p-4 border border-secondary w-64" style={{backgroundColor: "#D6D5E6"}}>
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      <div className="flex items-center mb-2">
        <ListTodo className="w-5 h-5 mr-2" />
        <h3 className="text-lg font-semibold">Sub Task</h3>
      </div>
      <p className="text-sm font-medium mb-2">
        {data.label}
      </p>
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
    </div>
  )
}

const TestNode = ({ data }) => {
  return (
    <div className="bg-accent text-accent-foreground rounded-lg shadow-md p-4 border border-accent w-48">
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      <div className="flex items-center mb-2">
        <TestTube2 className="w-5 h-5 mr-2" />
        <h3 className="text-lg font-semibold">Tests</h3>
      </div>
      <p className="text-sm font-medium text-center">
        {data.description}
      </p>
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
    </div>
  )
}

const nodeTypes = {
  mainTask: memo(MainTaskNode),
  subTask: memo(SubTaskNode),
  test: memo(TestNode),
  answer: memo(DisplayNode),
  codeAnswer: memo(CodeAnswerNode)
}
const layoutReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_NODE_AND_EDGE':
      const { newNode, newEdge } = action.payload;
      const nodesAfterAdd = [...state.nodes, newNode]; // Renamed to 'nodesAfterAdd'

      let updatedEdges;
      if (newEdge) {
        // Filter out any old edge that connects the same source and target as the new edge
        updatedEdges = state.edges.filter(edge => !(edge.source === newEdge.source && edge.target === newEdge.target));
        updatedEdges.push(newEdge);
      } else {
        updatedEdges = state.edges;
      }

      dagreGraph.setNode(newNode.id, { width: nodeWidth, height: nodeHeight });
      if (newEdge) {
        dagreGraph.setEdge(newEdge.source, newEdge.target);
      }

      dagre.layout(dagreGraph);

      const layoutedNodes = nodesAfterAdd.map(node => {
        const nodeWithPosition = dagreGraph.node(node.id);
        return {
          ...node,
          position: {
            x: nodeWithPosition.x - nodeWidth / 2,
            y: nodeWithPosition.y + nodeHeight / 2,
          },
          style: {
            color: "#333",
            border: "1px solid #222138",
            position: 'absolute',
            borderRadius: "8px",
            overflow: "auto",           // Added to handle large text
            wordBreak: "break-word",    // Added to handle large text
          },
        };
      });

      return { nodes: layoutedNodes, edges: updatedEdges };

    case 'UPDATE_NODE_TESTS':
      const { nodeId, passedTests, totalTests } = action.payload;

      // Update the specific node's test data
      const nodesAfterTestUpdate = state.nodes.map(node => { // Renamed to 'nodesAfterTestUpdate'
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              passedTests,
              totalTests,
              hasTests: totalTests > 0
            }
          };
        }
        return node;
      });

      return { ...state, nodes: nodesAfterTestUpdate };

    case 'UPDATE_NODES':
      return { ...state, nodes: action.payload };

    case 'UPDATE_EDGES':
      return { ...state, edges: action.payload };

    default:
      return state;
  }
};

const theme = createTheme({
  palette: {
    primary: {
      main: '#FF69B4',
    },
    secondary: {
      main: '#1E90FF',
    },
    background: {
      default: '#FFFFFF',
      paper: '#F5F5F5',  // Changed to light grey
    },
    text: {
      primary: '#000000', // Changed to black text
      secondary: '#FF69B4',
    },
  },
  typography: {
    fontFamily: '"Fira Code", monospace, bold',
    h1: {
      fontSize: '6rem',
      fontWeight: 900,
      marginBottom: '40px',
    },
    body1: {
      fontSize: '1rem',
      color: '#FFFFFF',
    },
    body2: {
      fontSize: '0.875rem',
      color: '#FF69B4',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          fontFamily: '"Playfair Display", serif', // Classy and minimalistic font
          color: '#000000', // Black text on yellow button
          backgroundColor: '#FFEB3B', // Yellow button background
          '&:hover': {
            backgroundColor: '#FFD700', // Darker yellow on hover
          },
        },
      },
    },
  },
  
});

function HomePage() {
  const [state, dispatch] = useReducer(layoutReducer, { nodes: [], edges: [] });
  const [isLoaded, setIsLoaded] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [questionInput, setQuestionInput] = useState('');
  const { fitView } = useReactFlow();
  const nodesInitialized = useNodesInitialized();
  const reactFlowInstanceRef = useRef(null);
  const reactFlowInstance = useReactFlow();


  

// ... (in your App component)

const handleSubmit = async (e) => {
  setIsExpanded(true);
  e.preventDefault();
  if (questionInput.trim()) {
    try {
      const response = await axios.post('http://localhost:5088/self-healing', {
        method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
        question: questionInput
      });

      if (response.data.status === "completed") {
        console.log("Question processed successfully");
        
        // Expand the view after submitting
        setIsExpanded(true);  // Make sure this line is present and working
        
        setChatMessages([...chatMessages, { text: questionInput, sender: 'user' }]);
        setQuestionInput('');
      } else {
        console.error("Unexpected response from server");
      }
    } catch (error) {
      console.error("Error submitting question:", error);
    }
  }
};
  const onNodesChange = (changes) => {
    dispatch({
      type: 'UPDATE_NODES',
      payload: applyNodeChanges(changes, state.nodes)
    });
  };

  const onEdgesChange = (changes) => {
    dispatch({
      type: 'UPDATE_EDGES',
      payload: applyEdgeChanges(changes, state.edges)
    });
  };

  const handleExpandClick = () => {
    setIsExpanded(true);
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (chatInput.trim()) {
      // Add user message to chat messages
      const userMessage = chatInput;
      setChatMessages([...chatMessages, { text: userMessage, sender: 'user' }]);
      setChatInput('');

      setIsProcessing(true)

      try {
        const response = await axios.post('http://localhost:5088/self-healing', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          question: userMessage, // Send the chat input
        });
  
        if (response.data.status === "completed") {
          console.log("Chat message processed successfully");
  

        // Add backend response to chat messages (aligned left)
        setChatMessages([...chatMessages, { text: userMessage, sender: 'user' }, { text: response.data.answer, sender: 'backend' }]);
        } else {
          console.error("Unexpected response from server");
        }
      } catch (error) {
        console.error("Error submitting chat message:", error);
      }

      setIsProcessing(false)
    }
  };


  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      setChatInput(event.target.value)
      handleChatSubmit(event)
    }
  }

  useEffect(() => {
    const handleUpdate = (data) => {
      console.log('Received update:', data);
      const newNode = {
        id: data.id,
        type: data.type,
        data: data.imageUrl ? { imageUrl: data.imageUrl } : { label: data.label }
      };
  
      const newEdge = data.parentId ? { id: `${data.parentId}-${data.id}`, source: data.parentId, target: data.id, animated: true } : null;
  
      dispatch({ type: 'ADD_NODE_AND_EDGE', payload: { newNode, newEdge } });

      reactFlowInstance.fitView();

    };
  
    socket.on('update', handleUpdate);
  
    setIsLoaded(true);

  
    return () => {
      socket.off('update', handleUpdate);
    };
  }, []);

  useEffect(() => {
    // Listen for the test updates from the backend
    socket.on('testUpdate', (data) => {
      const { nodeId, passedTests, totalTests } = data;
  
      // Update the specific node with the new test data
      dispatch({
        type: 'UPDATE_NODE_TESTS',
        payload: {
          nodeId,
          passedTests,
          totalTests
        }
      });
    });
  
    return () => {
      socket.off('testUpdate');
    };
  }, []);
  


  return (
    <ThemeProvider theme={theme}>
  <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'row', backgroundColor: '#f4f4f9' }}>
    {/* Chat Panel - 50% */}
    <Box sx={{ width: '50%', height: '100%', borderRight: '1px solid #e0e0e0', display: 'flex', flexDirection: 'column', backgroundColor: '#ffffff' }}>
      {/* Title Section */}
      <Box sx={{ borderBottom: '1px solid #e0e0e0', p: 2, backgroundColor: '#fafafa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#333' }}>
          show-me-bot
        </Typography>
      </Box>

      {/* Chat Messages */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 3 }}>
        {chatMessages.map((msg, index) => (
          <Box key={index} sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start', // Align user messages to the right
            mb: 2  // Added margin-bottom to space out the messages
          }}>
            <Typography style={{ whiteSpace: 'pre-line' }} sx={{
              textAlign: msg.sender === 'user' ? 'right' : 'left',
              color: msg.sender === 'user' ? '#1976d2' : '#333',
              backgroundColor: msg.sender === 'user' ? '#e3f2fd' : '#f0f0f0',
              padding: '10px 15px', // Adjusted padding for better aesthetics
              borderRadius: '12px',
              display: 'inline-block',
              maxWidth: '75%',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)', // Added shadow for better visual separation
              position: 'relative'
            }}>
              {msg.text}
            </Typography>
            {msg.sender !== 'user' ? (
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "row",
                  alignItems: "flex-start",
                  paddingY: 1,
                  ml: 0.5,
                  color: "#555",
                }}
              >
                <CopyButton text={msg.text} />
              </Box>
            ) : null}
          </Box>
        ))}
        {isProcessing ? (
          <Typography sx={{
            textAlign: 'left',
            color: '#999',
            fontSize: '0.8rem',
          }}>
            <AutorenewIcon
              sx={{
                animation: 'spin 1s linear infinite',
                '@keyframes spin': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' },
                },
                fontSize: '0.8rem',
              }}
            /> Processing...
          </Typography>
        ) : null}
      </Box>

      {/* Input Section */}
      <Box component="form" onSubmit={handleChatSubmit} sx={{ p: 2, borderTop: '1px solid #e0e0e0', backgroundColor: '#fafafa' }}>
        <TextField
          multiline
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={chatInput}
          maxRows={7}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyDown={handleKeyDown}
          InputProps={{
            sx: { borderRadius: '12px' }
          }}
        />
      </Box>
    </Box>

    {/* Graph Panel - 50% */}
    <Box sx={{ width: '50%', height: '100%', p: 2, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f9fafc' }}>

      <ReactFlowProvider>
        <ReactFlow 
          nodes={state.nodes} 
          edges={state.edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          connectionLineType={ConnectionLineType.SmoothStep}
          fitView
          minZoom={0.1}
        >
          <Background variant="dots" color="#000000" gap={20} />
          <Controls />
        </ReactFlow>
      </ReactFlowProvider>
    </Box>
  </Box>
</ThemeProvider>


  );
}

function FlowWithProvider(props) {
  return (
    <ReactFlowProvider>
      <App {...props} />
    </ReactFlowProvider>
  );
}

// export default FlowWithProvider;

function App() {
  return (
    <ReactFlowProvider>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/software" element={<SoftwareFlowWithProvider />} />
        </Routes>
      </Router>
    </ReactFlowProvider>
  );
}

export default App;

