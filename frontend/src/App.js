import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import theme from './theme';

// Layout and components
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import EnhancedDashboard from './components/EnhancedDashboard';
import AgentList from './components/AgentList';
import TaskList from './components/TaskList';
import TaskDetails from './components/TaskDetails';
import CreateTask from './components/CreateTask';
import EditTask from './components/EditTask';
import CreateAgent from './components/CreateAgent';
import AgentDetails from './components/AgentDetails';
import BlockchainExplorer from './components/BlockchainExplorer';
import TransactionDetails from './components/TransactionDetails';
import BlockDetails from './components/BlockDetails';
import TaskCollaboration from './components/TaskCollaboration';
import CollaborationDetails from './components/CollaborationDetails';
import StartCollaboration from './components/StartCollaboration';
import ConversationViewer from './components/ConversationViewer';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<EnhancedDashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/agents" element={<AgentList />} />
            <Route path="/agents/new" element={<CreateAgent />} />
            <Route path="/agents/:agentId" element={<AgentDetails />} />
            <Route path="/tasks" element={<TaskList />} />
            <Route path="/tasks/new" element={<CreateTask />} />
            <Route path="/tasks/:taskId" element={<TaskDetails />} />
            <Route path="/tasks/:taskId/edit" element={<EditTask />} />
            <Route path="/tasks/:taskId/collaborate" element={<TaskCollaboration />} />
            <Route path="/tasks/:taskId/start-collaboration" element={<StartCollaboration />} />
            <Route path="/tasks/:taskId/conversations" element={<ConversationViewer />} />
            <Route path="/tasks/:taskId/conversations/:conversationId" element={<ConversationViewer />} />
            <Route path="/collaboration/:collaborationId" element={<CollaborationDetails />} />
            <Route path="/blockchain" element={<BlockchainExplorer />} />
            <Route path="/blockchain/transactions/:txHash" element={<TransactionDetails />} />
            <Route path="/blockchain/blocks/:blockNumber" element={<BlockDetails />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;