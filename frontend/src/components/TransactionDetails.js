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
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Alert,
  Link
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ContentCopy as ContentCopyIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
  OpenInNew as OpenInNewIcon
} from '@mui/icons-material';
import { api, blockchainApi } from '../services/api';

// 交易状态芯片组件
const TransactionStatusChip = ({ status }) => {
  let color = 'default';
  let icon = <PendingIcon />;
  
  switch (status) {
    case 'confirmed':
      color = 'success';
      icon = <CheckCircleIcon />;
      break;
    case 'pending':
      color = 'warning';
      icon = <PendingIcon />;
      break;
    case 'failed':
      color = 'error';
      icon = <ErrorIcon />;
      break;
    default:
      break;
  }
  
  return (
    <Chip 
      icon={icon} 
      label={status.charAt(0).toUpperCase() + status.slice(1)} 
      color={color} 
      size="small" 
      sx={{ ml: 1 }}
    />
  );
};

// 交易详情组件
const TransactionDetails = () => {
  const { txHash } = useParams();
  const [transaction, setTransaction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // 获取交易详情
  useEffect(() => {
    const fetchTransactionDetails = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await blockchainApi.getTransactionByHash(txHash);
        setTransaction(response);
      } catch (err) {
        console.error("Error fetching transaction details:", err);
        setError("Failed to load transaction details. Please try again later.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchTransactionDetails();
  }, [txHash]);

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

  // 查看区块详情
  const handleViewBlock = (blockNumber) => {
    navigate(`/blockchain/blocks/${blockNumber}`);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !transaction) {
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
          {error || "Transaction not found"}
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
          Transaction Details
          <TransactionStatusChip status={transaction.status} />
        </Typography>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }} variant="outlined">
        <Typography variant="h6" gutterBottom>
          Overview
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Transaction Hash:
              </Typography>
              <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                {transaction.tx_hash}
              </Typography>
              <Tooltip title="Copy to clipboard">
                <IconButton size="small" onClick={() => copyToClipboard(transaction.tx_hash)}>
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Block:
              </Typography>
              <Link 
                component="button"
                variant="body2"
                onClick={() => handleViewBlock(transaction.block_number)}
                underline="hover"
              >
                {transaction.block_number}
              </Link>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Timestamp:
              </Typography>
              <Typography variant="body2">
                {formatTimestamp(transaction.timestamp)}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                From:
              </Typography>
              <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                {transaction.from_address}
              </Typography>
              <Tooltip title="Copy to clipboard">
                <IconButton size="small" onClick={() => copyToClipboard(transaction.from_address)}>
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                To:
              </Typography>
              <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                {transaction.to_address}
              </Typography>
              <Tooltip title="Copy to clipboard">
                <IconButton size="small" onClick={() => copyToClipboard(transaction.to_address)}>
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Value:
              </Typography>
              <Typography variant="body2">
                {transaction.value}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Gas Used:
              </Typography>
              <Typography variant="body2">
                {transaction.gas_used?.toLocaleString()}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Gas Price:
              </Typography>
              <Typography variant="body2">
                {transaction.gas_price}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Total Fee:
              </Typography>
              <Typography variant="body2">
                {transaction.total_fee}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }} variant="outlined">
        <Typography variant="h6" gutterBottom>
          Event Details
        </Typography>
        <Box sx={{ mb: 2 }}>
          <Chip 
            label={transaction.event_type} 
            color="primary" 
            variant="outlined" 
          />
        </Box>
        <Grid container spacing={2}>
          {transaction.event_data && Object.entries(transaction.event_data).map(([key, value]) => (
            <Grid item xs={12} sm={6} key={key}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                  {key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')}:
                </Typography>
                <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>

      <Paper sx={{ p: 3 }} variant="outlined">
        <Typography variant="h6" gutterBottom>
          Technical Details
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Input Data:
              </Typography>
              <Box sx={{ 
                maxHeight: '100px', 
                overflow: 'auto', 
                backgroundColor: 'rgba(0, 0, 0, 0.03)', 
                p: 1, 
                borderRadius: 1,
                fontFamily: 'monospace',
                fontSize: '0.75rem',
                wordBreak: 'break-all'
              }}>
                {transaction.input_data || '0x'}
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ width: 180 }}>
                Confirmations:
              </Typography>
              <Typography variant="body2">
                {transaction.confirmations}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default TransactionDetails;