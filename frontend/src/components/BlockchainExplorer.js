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
  Tabs,
  Tab,
  TextField,
  Button,
  Chip,
  CircularProgress,
  Snackbar,
  Alert,
  Grid,
  Card,
  CardContent,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  ArrowForward as ArrowForwardIcon,
  ContentCopy as ContentCopyIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
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
      variant="outlined"
    />
  );
};

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

// 区块链浏览器组件
const BlockchainExplorer = () => {
  const [tabValue, setTabValue] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [blocks, setBlocks] = useState([]);
  const [events, setEvents] = useState([]);
  const [eventsTotal, setEventsTotal] = useState(0);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const navigate = useNavigate();

  // 获取事件数据的独立函数（支持分页）
  const fetchEvents = async (currentPage = 0, currentRowsPerPage = 10) => {
    try {
      const eventsResponse = await blockchainApi.getEvents({
        limit: currentRowsPerPage,
        offset: currentPage * currentRowsPerPage
      });
      
      // 检查API响应
      if (eventsResponse.note && eventsResponse.note.includes("mock data")) {
        console.log("Backend returned mock events data");
        setEvents(eventsResponse.events || []);
        setEventsTotal(eventsResponse.total || 0);
        return true; // 表示有错误
      } else if (eventsResponse.events) {
        // 真实的Ganache事件数据
        console.log("Using real Ganache events data");
        setEvents(eventsResponse.events);
        setEventsTotal(eventsResponse.total || eventsResponse.events.length);
        return false;
      } else {
        // 连接正常但没有事件数据，显示空状态
        console.log("No events found in blockchain - this is normal if no contract events have been triggered");
        setEvents([]);
        setEventsTotal(0);
        return false;
      }
    } catch (err) {
      console.error("Error fetching events:", err);
      // API调用失败时使用mock数据
      const mockEventsData = blockchainApi.generateMockEvents();
      setEvents(mockEventsData.events || []);
      setEventsTotal(mockEventsData.total || (mockEventsData.events || []).length);
      return true; // 表示有错误
    }
  };

  // 获取区块链数据
  const fetchBlockchainData = async () => {
    setLoading(true);
    setError(null);
    
    // 独立获取每个数据源，这样可以混合使用真实数据和mock数据
    let hasErrors = false;
    
    // 获取交易列表 (支持自动回退到Mock数据)
    try {
      const txResponse = await blockchainApi.getTransactions({ 
        limit: 100, 
        offset: 0,
        event_type: filterType !== 'all' ? filterType : undefined
      });
      
      // 检查API响应
      if (txResponse.note && txResponse.note.includes("mock data")) {
        console.log("Backend returned mock data due to connection issues");
        setTransactions(txResponse.transactions || []);
        hasErrors = true;
      } else if (txResponse.transactions && txResponse.transactions.length > 0) {
        // 真实的Ganache数据，需要过滤掉包含success字段的包装对象
        console.log("Using real Ganache transaction data");
        const cleanTransactions = txResponse.transactions.map(tx => {
          // 如果交易数据被包装在success对象中，提取实际数据
          if (tx.success !== undefined) {
            const { success, ...cleanTx } = tx;
            return cleanTx;
          }
          return tx;
        });
        setTransactions(cleanTransactions);
      } else {
        // 连接正常但没有交易数据，显示空状态
        console.log("No transactions found in blockchain");
        setTransactions([]);
      }
    } catch (err) {
      console.error("Error fetching transactions:", err);
      hasErrors = true;
      // 交易API失败时使用mock数据
      const mockTxData = blockchainApi.generateMockTransactions();
      setTransactions(mockTxData.transactions || []);
    }
    
    // 获取区块链统计数据 (真实数据)
    try {
      const statsResponse = await blockchainApi.getBlockchainStats();
      setStats({
        blockchain: statsResponse
      });
    } catch (err) {
      console.error("Error fetching blockchain stats:", err);
      hasErrors = true;
      // 统计API失败时设置断连状态
      setStats({
        blockchain: {
          transaction_count: 0,
          block_count: 0,
          latest_block: 0,
          avg_block_time: 0.0,
          avg_transactions_per_block: 0.0,
          agent_count: 0,
          task_count: 0,
          learning_event_count: 0,
          connected: false
        }
      });
    }
    
    // 获取区块数据 (需要根据连接状态智能处理)
    try {
      const blocksResponse = await blockchainApi.getBlocks({
        limit: 100,  // 增加到100个区块
        offset: 0
      });
      
      // 检查API响应
      if (blocksResponse.note && blocksResponse.note.includes("mock data")) {
        console.log("Backend returned mock blocks data");
        setBlocks(blocksResponse.blocks || []);
        hasErrors = true;
      } else if (blocksResponse.blocks && blocksResponse.blocks.length > 0) {
        // 真实的Ganache数据
        console.log("Using real Ganache blocks data");
        setBlocks(blocksResponse.blocks);
      } else {
        // 连接正常但没有区块数据，显示空状态
        console.log("No blocks found in blockchain");
        setBlocks([]);
      }
    } catch (err) {
      console.error("Error fetching blocks:", err);
      hasErrors = true;
      // API调用失败时使用mock数据
      const mockBlocksData = blockchainApi.generateMockBlocks();
      setBlocks(mockBlocksData.blocks || []);
    }
    
    // 获取事件数据 (需要根据连接状态智能处理)
    const eventsHasError = await fetchEvents(page, rowsPerPage);
    if (eventsHasError) {
      hasErrors = true;
    }
    
    // 只有在有错误时才显示错误信息
    if (hasErrors) {
      setError("Some blockchain data sources are using fallback data.");
    }
    
    setLoading(false);
  };

  // 初始加载和刷新数据
  useEffect(() => {
    fetchBlockchainData();
    
    // 设置定期刷新 - 改为2分钟刷新一次
    const interval = setInterval(fetchBlockchainData, 120000);
    return () => clearInterval(interval);
  }, []); // 移除filterType依赖，避免频繁刷新
  
  // 单独处理filterType变化
  useEffect(() => {
    if (filterType !== 'all') {
      fetchBlockchainData();
    }
  }, [filterType]);

  // 处理标签页变化
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setPage(0);
  };

  // 处理页面变化
  const handleChangePage = async (event, newPage) => {
    setPage(newPage);
    // 如果当前在events标签页，需要重新获取数据
    if (tabValue === 2) {
      setLoading(true);
      await fetchEvents(newPage, rowsPerPage);
      setLoading(false);
    }
  };

  // 处理每页行数变化
  const handleChangeRowsPerPage = async (event) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    setRowsPerPage(newRowsPerPage);
    setPage(0);
    // 如果当前在events标签页，需要重新获取数据
    if (tabValue === 2) {
      setLoading(true);
      await fetchEvents(0, newRowsPerPage);
      setLoading(false);
    }
  };

  // 处理搜索
  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
    setPage(0);
  };

  // 处理交易点击
  const handleTransactionClick = (txHash) => {
    navigate(`/blockchain/transactions/${txHash}`);
  };

  // 处理区块点击
  const handleBlockClick = (blockNumber) => {
    navigate(`/blockchain/blocks/${blockNumber}`);
  };

  // 过滤交易
  const filteredTransactions = transactions.filter(tx => {
    if (!searchTerm) return true;
    
    const searchLower = searchTerm.toLowerCase();
    return (
      tx.tx_hash.toLowerCase().includes(searchLower) ||
      tx.from_address.toLowerCase().includes(searchLower) ||
      tx.to_address.toLowerCase().includes(searchLower) ||
      tx.event_type.toLowerCase().includes(searchLower)
    );
  });

  // 格式化时间戳
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    
    // 处理Unix时间戳（后端真实数据）和ISO字符串（mock数据）
    let date;
    if (typeof timestamp === 'number') {
      // Unix时间戳（秒）转换为毫秒
      date = new Date(timestamp * 1000);
    } else {
      // ISO字符串格式
      date = new Date(timestamp);
    }
    
    return date.toLocaleString();
  };

  // 格式化交易值
  const formatValue = (value) => {
    if (!value && value !== 0) return 'N/A';
    
    // 处理数字类型（后端真实数据）和字符串类型（mock数据）
    if (typeof value === 'number') {
      return `${value.toFixed(6)} ETH`;
    } else if (typeof value === 'string' && value.includes('ETH')) {
      return value; // 已经格式化的字符串
    } else {
      return `${parseFloat(value || 0).toFixed(6)} ETH`;
    }
  };

  // 渲染交易表格
  const renderTransactionsTable = () => {
    const displayTransactions = filteredTransactions
      .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
      
    return (
      <>
        <TableContainer component={Paper} elevation={0} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Transaction Hash</TableCell>
                <TableCell>Block</TableCell>
                <TableCell>Timestamp</TableCell>
                <TableCell>From</TableCell>
                <TableCell>To</TableCell>
                <TableCell>Value</TableCell>
                <TableCell>Event Type</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {displayTransactions.length > 0 ? (
                displayTransactions.map((tx) => (
                  <TableRow 
                    key={tx.tx_hash}
                    hover
                    onClick={() => handleTransactionClick(tx.tx_hash)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>
                      <ShortAddress address={tx.tx_hash} />
                    </TableCell>
                    <TableCell>{tx.block_number}</TableCell>
                    <TableCell>{formatTimestamp(tx.timestamp)}</TableCell>
                    <TableCell>
                      <ShortAddress address={tx.from_address} />
                    </TableCell>
                    <TableCell>
                      <ShortAddress address={tx.to_address} />
                    </TableCell>
                    <TableCell>{formatValue(tx.value)}</TableCell>
                    <TableCell>
                      <Chip 
                        label={tx.event_type} 
                        size="small" 
                        color="primary" 
                        variant="outlined" 
                      />
                    </TableCell>
                    <TableCell>
                      <TransactionStatusChip status={tx.status} />
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    No transactions found
                  </TableCell>
                </TableRow>
              )}
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
    );
  };

  // 渲染区块表格
  const renderBlocksTable = () => {
    const displayBlocks = blocks
      .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
      
    return (
      <>
        <TableContainer component={Paper} elevation={0} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Block Number</TableCell>
                <TableCell>Block Hash</TableCell>
                <TableCell>Timestamp</TableCell>
                <TableCell>Transactions</TableCell>
                <TableCell>Miner</TableCell>
                <TableCell>Gas Used</TableCell>
                <TableCell>Size</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {displayBlocks.length > 0 ? (
                displayBlocks.map((block) => (
                  <TableRow 
                    key={block.block_number || block.number}
                    hover
                    onClick={() => handleBlockClick(block.block_number || block.number)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>{block.block_number || block.number}</TableCell>
                    <TableCell>
                      <ShortAddress address={block.hash} />
                    </TableCell>
                    <TableCell>{formatTimestamp(block.timestamp)}</TableCell>
                    <TableCell>{block.transaction_count || block.transactions}</TableCell>
                    <TableCell>
                      <ShortAddress address={block.miner} />
                    </TableCell>
                    <TableCell>{(block.gas_used || 0).toLocaleString()}</TableCell>
                    <TableCell>{((block.size || 0) / 1000).toFixed(2)} KB</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No blocks found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={blocks.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </>
    );
  };

  // 渲染事件表格
  const renderEventsTable = () => {
    return (
      <>
        <TableContainer component={Paper} elevation={0} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Event Name</TableCell>
                <TableCell>Contract</TableCell>
                <TableCell>Block Number</TableCell>
                <TableCell>Transaction Hash</TableCell>
                <TableCell>Timestamp</TableCell>
                <TableCell>Parameters</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {events.length > 0 ? (
                events.map((event, index) => (
                  <TableRow 
                    key={event.event_id || `${event.tx_hash}-${index}`}
                    hover
                    onClick={() => handleTransactionClick(event.tx_hash)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>
                      <Chip 
                        label={event.event_name} 
                        size="small" 
                        color="primary" 
                        variant="outlined" 
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={event.contract_name || 'Unknown'} 
                        size="small" 
                        color="secondary" 
                        variant="outlined" 
                      />
                    </TableCell>
                    <TableCell>{event.block_number}</TableCell>
                    <TableCell>
                      <ShortAddress address={event.tx_hash} />
                    </TableCell>
                    <TableCell>{formatTimestamp(event.timestamp)}</TableCell>
                    <TableCell>
                      {Object.entries(event.parameters || event.data || {}).map(([key, value]) => (
                        <Chip 
                          key={key}
                          label={`${key}: ${String(value).substring(0, 20)}${String(value).length > 20 ? '...' : ''}`} 
                          size="small" 
                          sx={{ m: 0.25 }}
                        />
                      ))}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No events found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={eventsTotal}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </>
    );
  };

  // 渲染区块链统计卡片
  const renderStatsCards = () => {
    if (!stats) return null;
    
    return (
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Transactions
              </Typography>
              <Typography variant="h4" component="div">
                {stats.blockchain?.transaction_count?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Blocks
              </Typography>
              <Typography variant="h4" component="div">
                {stats.blockchain?.block_count?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Latest Block
              </Typography>
              <Typography variant="h4" component="div">
                #{stats.blockchain?.latest_block?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Network Status
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Chip 
                  icon={stats.blockchain?.connected ? <CheckCircleIcon /> : <ErrorIcon />} 
                  label={stats.blockchain?.connected ? "Connected" : "Disconnected"} 
                  color={stats.blockchain?.connected ? "success" : "error"} 
                  variant="outlined"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Blockchain Explorer
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchBlockchainData}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>
      
      {renderStatsCards()}
      
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Transactions" />
          <Tab label="Blocks" />
          <Tab label="Events" />
        </Tabs>
      </Paper>
      
      {tabValue === 0 && (
        <Box sx={{ mb: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                variant="outlined"
                size="small"
                placeholder="Search by hash, address, or event type"
                value={searchTerm}
                onChange={handleSearch}
                InputProps={{
                  startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                select
                fullWidth
                variant="outlined"
                size="small"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                SelectProps={{
                  native: true
                }}
              >
                <option value="all">All Event Types</option>
                <option value="TaskCreated">Task Created</option>
                <option value="TaskAssigned">Task Assigned</option>
                <option value="TaskCompleted">Task Completed</option>
                <option value="AgentRegistered">Agent Registered</option>
                <option value="LearningEvent">Learning Event</option>
              </TextField>
            </Grid>
          </Grid>
        </Box>
      )}
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {tabValue === 0 && renderTransactionsTable()}
          {tabValue === 1 && renderBlocksTable()}
          {tabValue === 2 && renderEventsTable()}
        </>
      )}
      
      <Snackbar 
        open={!!error} 
        autoHideDuration={6000} 
        onClose={() => setError(null)}
      >
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default BlockchainExplorer;