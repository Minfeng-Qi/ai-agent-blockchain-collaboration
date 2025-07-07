import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import theme from './theme';

// Layout and components
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import AgentList from './components/AgentList';
import TaskList from './components/TaskList';
import TaskDetails from './components/TaskDetails';
import CreateTask from './components/CreateTask';
import LearningDashboard from './components/LearningDashboard';
import AgentDetails from './components/AgentDetails';
import BlockchainExplorer from './components/BlockchainExplorer';
import TransactionDetails from './components/TransactionDetails';
import BlockDetails from './components/BlockDetails';
import TaskCollaboration from './components/TaskCollaboration';
import CollaborationDetails from './components/CollaborationDetails';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/agents" element={<AgentList />} />
            <Route path="/agents/:agentId" element={<AgentDetails />} />
            <Route path="/tasks" element={<TaskList />} />
            <Route path="/tasks/new" element={<CreateTask />} />
            <Route path="/tasks/:taskId" element={<TaskDetails />} />
            <Route path="/tasks/:taskId/collaborate" element={<TaskCollaboration />} />
            <Route path="/collaboration/:collaborationId" element={<CollaborationDetails />} />
            <Route path="/learning" element={<LearningDashboard />} />
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