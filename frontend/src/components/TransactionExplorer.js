import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  CircularProgress,
  Chip,
  TextField,
  Button,
  IconButton,
  Tooltip,
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  ContentCopy as CopyIcon,
  ExpandMore as ExpandMoreIcon,
  CallMade as CallMadeIcon,
  CallReceived as CallReceivedIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { systemApi } from '../services/api';

// 格式化地址，只显示前6位和后4位
const formatAddress = (address) => {
  if (!address) return '';
  return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
};

// 格式化时间戳
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '';
  return new Date(timestamp * 1000).toLocaleString();
};

// 格式化交易类型
const getTransactionType = (tx) => {
  if (tx.event === 'AgentRegistered') return 'Agent Registration';
  if (tx.event === 'TaskCreated') return 'Task Creation';
  if (tx.event === 'TaskAssigned') return 'Task Assignment';
  if (tx.event === 'TaskStatusUpdated') return 'Task Status Update';
  if (tx.event === 'LearningEventRecorded') return 'Learning Event';
  return 'Transaction';
};

// 获取交易颜色
const getTransactionColor = (tx) => {
  if (tx.event === 'AgentRegistered') return 'primary';
  if (tx.event === 'TaskCreated') return 'secondary';
  if (tx.event === 'TaskAssigned') return 'warning';
  if (tx.event === 'TaskStatusUpdated') return 'info';
  if (tx.event === 'LearningEventRecorded') return 'success';
  return 'default';
};

// 交易详情组件
const TransactionDetails = ({ transaction }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Snackbar
        open={copied}
        autoHideDuration={2000}
        onClose={() => setCopied(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert severity="success" sx={{ width: '100%' }}>
          Copied to clipboard!
        </Alert>
      </Snackbar>

      <Typography variant="h6" gutterBottom>
        Transaction Details
      </Typography>

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" sx={{ mr: 1 }}>Hash:</Typography>
        <Typography variant="body1" sx={{ fontFamily: 'monospace', mr: 1 }}>
          {transaction.hash}
        </Typography>
        <IconButton size="small" onClick={() => copyToClipboard(transaction.hash)}>
          <CopyIcon fontSize="small" />
        </IconButton>
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" sx={{ mr: 1 }}>Block:</Typography>
        <Typography variant="body1">{transaction.blockNumber}</Typography>
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" sx={{ mr: 1 }}>Timestamp:</Typography>
        <Typography variant="body1">{formatTimestamp(transaction.timestamp)}</Typography>
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" sx={{ mr: 1 }}>From:</Typography>
        <Typography variant="body1" sx={{ fontFamily: 'monospace', mr: 1 }}>
          {transaction.from}
        </Typography>
        <IconButton size="small" onClick={() => copyToClipboard(transaction.from)}>
          <CopyIcon fontSize="small" />
        </IconButton>
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" sx={{ mr: 1 }}>To:</Typography>
        <Typography variant="body1" sx={{ fontFamily: 'monospace', mr: 1 }}>
          {transaction.to}
        </Typography>
        <IconButton size="small" onClick={() => copyToClipboard(transaction.to)}>
          <CopyIcon fontSize="small" />
        </IconButton>
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" sx={{ mr: 1 }}>Gas Used:</Typography>
        <Typography variant="body1">{transaction.gasUsed}</Typography>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>Event:</Typography>
        <Chip 
          label={transaction.event} 
          color={getTransactionColor(transaction)} 
          variant="outlined" 
        />
      </Box>

      <Typography variant="subtitle1" gutterBottom>Parameters:</Typography>
      <Paper variant="outlined" sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
        <pre style={{ margin: 0, overflow: 'auto' }}>
          {JSON.stringify(transaction.parameters, null, 2)}
        </pre>
      </Paper>
    </Box>
  );
};

const TransactionExplorer = () => {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await systemApi.getTransactions();
      if (response && response.transactions) {
        setTransactions(response.transactions);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Error fetching transactions:', error);
      setError('Failed to fetch transactions. Using sample data instead.');
      
      // 模拟数据
      const mockTransactions = [
        {
          hash: '0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234',
          blockNumber: 12345,
          timestamp: Math.floor(Date.now() / 1000) - 3600,
          from: '0x1234567890123456789012345678901234567890',
          to: '0x5FbDB2315678afecb367f032d93F642f64180aa3',
          gasUsed: 50000,
          event: 'AgentRegistered',
          parameters: {
            agentAddress: '0x1234567890123456789012345678901234567890',
            name: 'DataAnalysisAgent',
            timestamp: Math.floor(Date.now() / 1000) - 3600
          }
        },
        {
          hash: '0xefgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678',
          blockNumber: 12346,
          timestamp: Math.floor(Date.now() / 1000) - 2400,
          from: '0x9876543210987654321098765432109876543210',
          to: '0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512',
          gasUsed: 75000,
          event: 'TaskCreated',
          parameters: {
            taskId: 1,
            creator: '0x9876543210987654321098765432109876543210',
            title: 'Market Analysis',
            reward: 0.5
          }
        },
        {
          hash: '0xijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012',
          blockNumber: 12347,
          timestamp: Math.floor(Date.now() / 1000) - 1200,
          from: '0x1234567890123456789012345678901234567890',
          to: '0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512',
          gasUsed: 60000,
          event: 'TaskAssigned',
          parameters: {
            taskId: 1,
            assignedAgent: '0x1234567890123456789012345678901234567890'
          }
        },
        {
          hash: '0xmnop3456mnop3456mnop3456mnop3456mnop3456mnop3456mnop3456mnop3456',
          blockNumber: 12348,
          timestamp: Math.floor(Date.now() / 1000) - 600,
          from: '0x1234567890123456789012345678901234567890',
          to: '0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512',
          gasUsed: 55000,
          event: 'TaskStatusUpdated',
          parameters: {
            taskId: 1,
            status: 'completed'
          }
        },
        {
          hash: '0xqrst7890qrst7890qrst7890qrst7890qrst7890qrst7890qrst7890qrst7890',
          blockNumber: 12349,
          timestamp: Math.floor(Date.now() / 1000) - 300,
          from: '0x1234567890123456789012345678901234567890',
          to: '0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0',
          gasUsed: 80000,
          event: 'LearningEventRecorded',
          parameters: {
            eventId: 1,
            agentAddress: '0x1234567890123456789012345678901234567890',
            eventType: 'task_completion',
            timestamp: Math.floor(Date.now() / 1000) - 300
          }
        }
      ];
      
      setTransactions(mockTransactions);
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearch = () => {
    // 实现搜索功能
  };

  const handleTransactionClick = (transaction) => {
    setSelectedTransaction(transaction);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
  };

  // 过滤交易
  const filteredTransactions = transactions.filter(tx => 
    tx.hash.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tx.from.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tx.to.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tx.event.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Transaction Explorer</Typography>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={fetchTransactions}
        >
          Refresh
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <TextField
            label="Search transactions"
            variant="outlined"
            fullWidth
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by hash, address, or event type"
            size="small"
            sx={{ mr: 2 }}
          />
          <Button
            variant="contained"
            startIcon={<SearchIcon />}
            onClick={handleSearch}
          >
            Search
          </Button>
        </Box>
      </Paper>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Box sx={{ p: 2 }}>
          <Alert severity="warning">{error}</Alert>
        </Box>
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table sx={{ minWidth: 650 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Hash</TableCell>
                  <TableCell>Block</TableCell>
                  <TableCell>Time</TableCell>
                  <TableCell>From</TableCell>
                  <TableCell>To</TableCell>
                  <TableCell>Type</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredTransactions
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((tx) => (
                    <TableRow
                      key={tx.hash}
                      hover
                      onClick={() => handleTransactionClick(tx)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell sx={{ fontFamily: 'monospace' }}>{formatAddress(tx.hash)}</TableCell>
                      <TableCell>{tx.blockNumber}</TableCell>
                      <TableCell>{formatTimestamp(tx.timestamp)}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <CallMadeIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography sx={{ fontFamily: 'monospace' }}>{formatAddress(tx.from)}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <CallReceivedIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography sx={{ fontFamily: 'monospace' }}>{formatAddress(tx.to)}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getTransactionType(tx)}
                          color={getTransactionColor(tx)}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={filteredTransactions.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </>
      )}

      <Dialog
        open={detailsOpen}
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogContent>
          {selectedTransaction && <TransactionDetails transaction={selectedTransaction} />}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TransactionExplorer;