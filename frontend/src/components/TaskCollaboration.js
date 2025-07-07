import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Container, Typography, Box, Paper, Button, CircularProgress, 
  Stepper, Step, StepLabel, Alert, Grid, Card, CardContent,
  Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions
} from '@mui/material';
import { api } from '../services/api';

const TaskCollaboration = () => {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [collaborating, setCollaborating] = useState(false);
  const [error, setError] = useState(null);
  const [collaboration, setCollaboration] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [openAgentUpdatesDialog, setOpenAgentUpdatesDialog] = useState(false);
  
  const steps = ['Select Task', 'Start Collaboration', 'View Results'];
  
  useEffect(() => {
    const fetchTask = async () => {
      try {
        setLoading(true);
        
        // Get task details
        const taskData = await api.getTaskById(taskId);
        setTask(taskData);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Error loading data. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchTask();
  }, [taskId]);
  
  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };
  
  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };
  
  const handleStartCollaboration = async () => {
    try {
      setCollaborating(true);
      setError(null);
      
      // Create collaboration
      const collaborationRequest = {
        task_data: {
          task_id: task.task_id,
          title: task.title,
          description: task.description,
          type: task.type,
          requirements: task.requirements,
          reward: task.reward,
          required_capabilities: task.required_capabilities
        }
      };
      
      // Create collaboration
      const createResponse = await api.createCollaboration(collaborationRequest);
      const collaborationId = createResponse.collaboration_id;
      
      // Run collaboration
      const collaborationResult = await api.runCollaboration(collaborationId, collaborationRequest);
      setCollaboration(collaborationResult);
      
      setCollaborating(false);
      handleNext();
    } catch (err) {
      console.error('Error starting collaboration:', err);
      setError('Error starting collaboration. Please try again later.');
      setCollaborating(false);
    }
  };
  
  const handleViewDetails = () => {
    if (collaboration) {
      navigate(`/collaboration/${collaboration.collaboration_id}`);
    }
  };
  
  const handleOpenDialog = () => {
    setOpenDialog(true);
  };
  
  const handleCloseDialog = () => {
    setOpenDialog(false);
  };
  
  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>{error}</Alert>
      </Container>
    );
  }
  
  if (!task) {
    return (
      <Container maxWidth="lg">
        <Alert severity="info" sx={{ mt: 4 }}>Task data not found</Alert>
      </Container>
    );
  }
  
  // Check if task status is not 'open'
  const isTaskNotOpen = task.status !== 'open';
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Task Collaboration
        </Typography>
        
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        <Paper sx={{ p: 3 }}>
          {activeStep === 0 && (
            <>
              <Typography variant="h5" gutterBottom>
                Task Details
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6">{task.title}</Typography>
                <Typography variant="body1" paragraph>
                  {task.description}
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle1">
                      <strong>Type:</strong> {task.type}
                    </Typography>
                    <Typography variant="subtitle1">
                      <strong>Status:</strong> {task.status}
                    </Typography>
                    <Typography variant="subtitle1">
                      <strong>Reward:</strong> {task.reward} ETH
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle1">
                      <strong>Created at:</strong> {new Date(task.created_at).toLocaleString()}
                    </Typography>
                    {task.deadline && (
                      <Typography variant="subtitle1">
                        <strong>Deadline:</strong> {new Date(task.deadline).toLocaleString()}
                      </Typography>
                    )}
                    <Typography variant="subtitle1">
                      <strong>Required capabilities:</strong> {task.required_capabilities?.join(', ')}
                    </Typography>
                  </Grid>
                </Grid>
                
                {isTaskNotOpen && (
                  <Alert severity="warning" sx={{ mt: 2 }}>
                    Collaboration can only be started for tasks with 'open' status. Current status: {task.status}
                  </Alert>
                )}
              </Box>
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button 
                  onClick={handleNext} 
                  variant="contained" 
                  color="primary"
                  disabled={isTaskNotOpen}
                >
                  Next
                </Button>
              </Box>
            </>
          )}
          
          {activeStep === 1 && (
            <>
              <Typography variant="h5" gutterBottom>
                Start Collaboration
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                The system will automatically select the most suitable agents to complete the task "{task.title}".
                Click the "Start Collaboration" button to initiate collaboration between agents.
              </Alert>
              
              <Typography variant="body1" paragraph>
                Agents will communicate via API to collaboratively solve the task. The entire conversation will be recorded on IPFS, and the hash will be stored on the blockchain.
              </Typography>
              
              <Typography variant="body1" paragraph>
                Collaboration may take some time, depending on the complexity of the task and the number of agents selected.
              </Typography>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
                <Button onClick={handleBack} variant="outlined" disabled={collaborating}>
                  Back
                </Button>
                <Button 
                  onClick={handleStartCollaboration} 
                  variant="contained" 
                  color="primary"
                  disabled={collaborating}
                >
                  {collaborating ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 1 }} />
                      Collaborating...
                    </>
                  ) : 'Start Collaboration'}
                </Button>
              </Box>
            </>
          )}
          
          {activeStep === 2 && (
            <>
              <Typography variant="h5" gutterBottom>
                Collaboration Results
              </Typography>
              
              {collaboration ? (
                <>
                  <Alert severity="success" sx={{ mb: 3 }}>
                    Collaboration completed successfully!
                  </Alert>
                  
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle1">
                      <strong>Collaboration ID:</strong> {collaboration.collaboration_id}
                    </Typography>
                    <Typography variant="subtitle1">
                      <strong>IPFS CID:</strong> {collaboration.ipfs_cid}
                    </Typography>
                    {collaboration.tx_hash && (
                      <Typography variant="subtitle1">
                        <strong>Blockchain Transaction Hash:</strong> {collaboration.tx_hash}
                      </Typography>
                    )}
                  </Box>
                  
                  <Button 
                    variant="contained" 
                    color="primary" 
                    onClick={handleViewDetails}
                    sx={{ mr: 2 }}
                  >
                    View Detailed Conversation
                  </Button>
                  
                  <Button 
                    variant="outlined" 
                    onClick={handleOpenDialog}
                    sx={{ mr: 2 }}
                  >
                    View Summary
                  </Button>
                  
                  {collaboration.agent_updates && collaboration.agent_updates.length > 0 && (
                    <Button 
                      variant="outlined"
                      color="secondary"
                      onClick={() => setOpenAgentUpdatesDialog(true)}
                    >
                      View Agent Updates
                    </Button>
                  )}
                </>
              ) : (
                <Alert severity="warning">
                  No collaboration results found. Please try again or contact the administrator.
                </Alert>
              )}
            </>
          )}
        </Paper>
      </Box>
      
      {/* Results Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>Collaboration Results Summary</DialogTitle>
        <DialogContent>
          {collaboration && collaboration.conversation && (
            <DialogContentText component="div">
              {/* Find the last assistant message as the result */}
              {(() => {
                const assistantMessages = collaboration.conversation.filter(msg => msg.role === 'assistant');
                const lastMessage = assistantMessages[assistantMessages.length - 1];
                
                if (lastMessage) {
                  return (
                    <Paper elevation={0} sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                      <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-wrap' }}>
                        {lastMessage.content}
                      </Typography>
                    </Paper>
                  );
                } else {
                  return <Alert severity="info">No result summary found</Alert>;
                }
              })()}
            </DialogContentText>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
          <Button onClick={handleViewDetails} variant="contained" color="primary">
            View Full Conversation
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Agent Updates Dialog */}
      <Dialog open={openAgentUpdatesDialog} onClose={() => setOpenAgentUpdatesDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Agent Performance Updates</DialogTitle>
        <DialogContent>
          {collaboration && collaboration.agent_updates && (
            <Box>
              <Typography variant="body1" gutterBottom>
                The following agents were automatically updated based on their collaboration performance:
              </Typography>
              
              {collaboration.agent_updates.map((update, index) => (
                <Card key={index} sx={{ mb: 2, border: '1px solid #e0e0e0' }}>
                  <CardContent>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="h6" color="primary">
                          Agent {update.agent_id.slice(-8)}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Performance Score:</strong> {update.performance_score.toFixed(1)}/100
                        </Typography>
                        <Typography variant="body2">
                          <strong>Update Type:</strong> {update.update_type}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        {update.metrics && (
                          <>
                            <Typography variant="body2">
                              <strong>Messages:</strong> {update.metrics.message_count}
                            </Typography>
                            <Typography variant="body2">
                              <strong>Avg Message Length:</strong> {update.metrics.average_message_length.toFixed(0)} chars
                            </Typography>
                            <Typography variant="body2">
                              <strong>Total Contribution:</strong> {update.metrics.total_content_length} chars
                            </Typography>
                          </>
                        )}
                      </Grid>
                      <Grid item xs={12}>
                        {update.transaction_hash && (
                          <Typography variant="caption" color="textSecondary">
                            Blockchain Record: {update.transaction_hash}
                          </Typography>
                        )}
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              ))}
              
              <Alert severity="info" sx={{ mt: 2 }}>
                These updates have been recorded on the blockchain and will affect future agent selection and performance tracking.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAgentUpdatesDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default TaskCollaboration;