import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  CircularProgress,
  Button,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Alert,
  Link
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ContentCopy as ContentCopyIcon,
  ArrowForward as ArrowForwardIcon,
  ArrowBack as ArrowLeftIcon
} from '@mui/icons-material';
import { api, blockchainApi } from '../services/api';

// 地址简写组件
const ShortAddress = ({ address }) => {
  const shortAddr = address ? `${address.substring(0, 6)}...${address.substring(address.length - 4)}` : 'N/A';
  
  const copyToClipboard = () => {
    navigator.clipboard.writeText(address);
  };
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <Typography variant="body2" component="span">
        {shortAddr}
      </Typography>
      <Tooltip title="Copy address">
        <IconButton size="small" onClick={copyToClipboard}>
          <ContentCopyIcon fontSize="inherit" />
        </IconButton>
      </Tooltip>
    </Box>
  );
};

// 区块详情组件
const BlockDetails = () => {
  const { blockNumber } = useParams();
  const [block, setBlock] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // 获取区块详情
  useEffect(() => {
    const fetchBlockDetails = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await blockchainApi.getBlockByNumber(blockNumber);
        setBlock(response);
        
        // 获取区块中的交易
        if (response.transactions > 0) {
          try {
            const txResponse = await blockchainApi.getTransactions({ 
              block_number: blockNumber,
              limit: 100,
              offset: 0
            });
            setTransactions(txResponse.transactions || []);
          } catch (err) {
            console.error("Error fetching block transactions:", err);
          }
        }
      } catch (err) {
        console.error("Error fetching block details:", err);
        setError("Failed to load block details. Please try again later.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchBlockDetails();
  }, [blockNumber]);

  // 复制到剪贴板
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  // 格式化时间戳
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  // 返回区块链浏览器
  const handleBack = () => {
    navigate('/blockchain');
  };

  // 查看前一个区块
  const handlePreviousBlock = () => {
    if (block && block.number > 0) {
      navigate(`/blockchain/blocks/${block.number - 1}`);
    }
  };

  // 查看后一个区块
  const handleNextBlock = () => {
    if (block) {
      navigate(`/blockchain/blocks/${block.number + 1}`);
    }
  };

  // 查看交易详情
  const handleViewTransaction = (txHash) => {
    navigate(`/blockchain/transactions/${txHash}`);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !block) {
    return (
      <Box sx={{ p: 3 }}>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={handleBack}
          sx={{ mb: 2 }}
        >
          Back to Explorer
        </Button>
        <Alert severity="error" sx={{ mt: 2 }}>
          {error || "Block not found"}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={handleBack}
          sx={{ mr: 2 }}
        >
          Back to Explorer
        </Button>
        <Typography variant="h5" component="h1">
          Block #{block.number}
        </Typography>
        <Box sx={{ ml: 'auto', display: 'flex' }}>
          <Button 
            startIcon={<ArrowLeftIcon />} 
            onClick={handlePreviousBlock}
            disabled={block.number <= 0}
            sx={{ mr: 1 }}
          >
            Previous
          </Button>
          <Button 
            endIcon={<ArrowForwardIcon />} 
            onClick={handleNextBlock}
          >
            Next
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }} variant="outlined">
        <Typography variant="h6" gutterBottom>
          Overview
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Block Hash:
              </Typography>
              <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                {block.hash}
              </Typography>
              <Tooltip title="Copy to clipboard">
                <IconButton size="small" onClick={() => copyToClipboard(block.hash)}>
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Parent Hash:
              </Typography>
              <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                {block.parent_hash}
              </Typography>
              <Tooltip title="Copy to clipboard">
                <IconButton size="small" onClick={() => copyToClipboard(block.parent_hash)}>
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Timestamp:
              </Typography>
              <Typography variant="body2">
                {formatTimestamp(block.timestamp)}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Transactions:
              </Typography>
              <Typography variant="body2">
                {block.transactions}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Mined By:
              </Typography>
              <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                {block.miner}
              </Typography>
              <Tooltip title="Copy to clipboard">
                <IconButton size="small" onClick={() => copyToClipboard(block.miner)}>
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Gas Used:
              </Typography>
              <Typography variant="body2">
                {block.gas_used?.toLocaleString()} ({((block.gas_used / block.gas_limit) * 100).toFixed(2)}%)
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Gas Limit:
              </Typography>
              <Typography variant="body2">
                {block.gas_limit?.toLocaleString()}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Difficulty:
              </Typography>
              <Typography variant="body2">
                {block.difficulty}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Block Reward:
              </Typography>
              <Typography variant="body2">
                {block.block_reward}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Size:
              </Typography>
              <Typography variant="body2">
                {(block.size / 1000).toFixed(2)} KB
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Nonce:
              </Typography>
              <Typography variant="body2">
                {block.nonce}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3 }} variant="outlined">
        <Typography variant="h6" gutterBottom>
          Transactions ({transactions.length})
        </Typography>
        {transactions.length > 0 ? (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Transaction Hash</TableCell>
                  <TableCell>From</TableCell>
                  <TableCell>To</TableCell>
                  <TableCell>Value</TableCell>
                  <TableCell>Event Type</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {transactions.map((tx) => (
                  <TableRow 
                    key={tx.tx_hash}
                    hover
                    onClick={() => handleViewTransaction(tx.tx_hash)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>
                      <ShortAddress address={tx.tx_hash} />
                    </TableCell>
                    <TableCell>
                      <ShortAddress address={tx.from_address} />
                    </TableCell>
                    <TableCell>
                      <ShortAddress address={tx.to_address} />
                    </TableCell>
                    <TableCell>{tx.value}</TableCell>
                    <TableCell>
                      <Chip 
                        label={tx.event_type} 
                        size="small" 
                        color="primary" 
                        variant="outlined" 
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Typography variant="body2" color="textSecondary" sx={{ py: 2, textAlign: 'center' }}>
            No transactions in this block
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default BlockDetails;