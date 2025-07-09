import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

function AgentLearningViz({ agentAddress }) {
  const [learningData, setLearningData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCapability, setSelectedCapability] = useState('all');

  useEffect(() => {
    if (!agentAddress) return;

    const fetchLearningData = async () => {
      try {
        setLoading(true);
        
        // Fetch agent learning data from API
        const response = await fetch(`http://localhost:8001/agents/${agentAddress}/learning`);
        if (!response.ok) {
          throw new Error('Failed to fetch agent learning data');
        }
        
        const data = await response.json();
        setLearningData(data);
        
        // Set default selected capability if available
        if (data.capabilities && data.capabilities.length > 0) {
          setSelectedCapability(data.capabilities[0].tag);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching agent learning data:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchLearningData();
    
    // Set up polling interval for real-time updates
    const interval = setInterval(fetchLearningData, 30000); // Update every 30 seconds
    
    return () => clearInterval(interval);
  }, [agentAddress]);

  if (loading) return <div className="loading">Loading learning data...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!learningData) return <div className="empty">No learning data available</div>;

  // Prepare capability evolution chart data
  const prepareCapabilityChartData = () => {
    if (!learningData.capabilityEvolution || learningData.capabilityEvolution.length === 0) {
      return null;
    }
    
    // Filter evolution data for selected capability or show all
    let evolutionData = learningData.capabilityEvolution;
    if (selectedCapability !== 'all') {
      evolutionData = evolutionData.filter(entry => entry.tag === selectedCapability);
    }
    
    // Group by capability tag
    const groupedByTag = {};
    evolutionData.forEach(entry => {
      if (!groupedByTag[entry.tag]) {
        groupedByTag[entry.tag] = [];
      }
      groupedByTag[entry.tag].push({
        timestamp: new Date(entry.timestamp * 1000).toLocaleString(),
        weight: entry.newWeight
      });
    });
    
    // Prepare datasets for chart
    const datasets = Object.keys(groupedByTag).map((tag, index) => {
      const color = getColorForIndex(index);
      return {
        label: tag,
        data: groupedByTag[tag].map(entry => entry.weight),
        borderColor: color,
        backgroundColor: `${color}33`, // Add transparency
        fill: false,
        tension: 0.1
      };
    });
    
    return {
      labels: groupedByTag[Object.keys(groupedByTag)[0]].map(entry => entry.timestamp),
      datasets
    };
  };

  // Prepare bidding strategy evolution chart data
  const prepareBiddingStrategyChartData = () => {
    if (!learningData.biddingStrategyEvolution || learningData.biddingStrategyEvolution.length === 0) {
      return null;
    }
    
    const timestamps = learningData.biddingStrategyEvolution.map(entry => 
      new Date(entry.timestamp * 1000).toLocaleString()
    );
    
    return {
      labels: timestamps,
      datasets: [
        {
          label: 'Confidence Factor',
          data: learningData.biddingStrategyEvolution.map(entry => entry.newConfidence),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          fill: false,
          tension: 0.1
        },
        {
          label: 'Risk Tolerance',
          data: learningData.biddingStrategyEvolution.map(entry => entry.newRiskTolerance),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          fill: false,
          tension: 0.1
        },
        {
          label: 'Task Score',
          data: learningData.biddingStrategyEvolution.map(entry => entry.taskScore),
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          fill: false,
          tension: 0.1
        }
      ]
    };
  };

  // Prepare learning curve chart data
  const prepareLearningCurveData = () => {
    if (!learningData.learningCurve || learningData.learningCurve.length === 0) {
      return null;
    }
    
    const dataPoints = learningData.learningCurve.map((score, index) => ({
      x: index + 1,
      y: score
    }));
    
    return {
      labels: dataPoints.map(point => point.x),
      datasets: [
        {
          label: 'Task Scores Over Time',
          data: dataPoints.map(point => point.y),
          borderColor: 'rgb(153, 102, 255)',
          backgroundColor: 'rgba(153, 102, 255, 0.2)',
          fill: false,
          tension: 0.1
        }
      ]
    };
  };

  // Helper function to generate colors
  const getColorForIndex = (index) => {
    const colors = [
      'rgb(75, 192, 192)',
      'rgb(255, 99, 132)',
      'rgb(54, 162, 235)',
      'rgb(255, 206, 86)',
      'rgb(153, 102, 255)',
      'rgb(255, 159, 64)',
      'rgb(199, 199, 199)'
    ];
    return colors[index % colors.length];
  };

  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        max: 100
      }
    },
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      }
    }
  };

  const capabilityChartData = prepareCapabilityChartData();
  const biddingStrategyChartData = prepareBiddingStrategyChartData();
  const learningCurveData = prepareLearningCurveData();

  return (
    <div className="agent-learning-viz">
      <h2>Agent Learning Visualization</h2>
      
      <div className="agent-stats">
        <div className="stat-item">
          <span className="stat-label">Reputation</span>
          <span className="stat-value">{learningData.reputation}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Workload</span>
          <span className="stat-value">{learningData.workload}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Tasks Completed</span>
          <span className="stat-value">{learningData.tasksCompleted || 0}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Avg. Score</span>
          <span className="stat-value">{learningData.averageScore || 0}</span>
        </div>
      </div>
      
      <div className="chart-section">
        <h3>Capability Evolution</h3>
        <div className="capability-selector">
          <label>
            Select Capability:
            <select 
              value={selectedCapability} 
              onChange={(e) => setSelectedCapability(e.target.value)}
            >
              <option value="all">All Capabilities</option>
              {learningData.capabilities && learningData.capabilities.map(cap => (
                <option key={cap.tag} value={cap.tag}>{cap.tag}</option>
              ))}
            </select>
          </label>
        </div>
        <div className="chart-container">
          {capabilityChartData ? (
            <Line data={capabilityChartData} options={chartOptions} height={300} />
          ) : (
            <div className="no-data">No capability evolution data available</div>
          )}
        </div>
      </div>
      
      <div className="chart-section">
        <h3>Bidding Strategy Evolution</h3>
        <div className="chart-container">
          {biddingStrategyChartData ? (
            <Line data={biddingStrategyChartData} options={chartOptions} height={300} />
          ) : (
            <div className="no-data">No bidding strategy evolution data available</div>
          )}
        </div>
      </div>
      
      <div className="chart-section">
        <h3>Learning Curve</h3>
        <div className="chart-container">
          {learningCurveData ? (
            <Line data={learningCurveData} options={chartOptions} height={300} />
          ) : (
            <div className="no-data">No learning curve data available</div>
          )}
        </div>
      </div>
      
      <div className="capabilities-table">
        <h3>Current Capabilities</h3>
        <table>
          <thead>
            <tr>
              <th>Capability</th>
              <th>Weight</th>
              <th>Change</th>
            </tr>
          </thead>
          <tbody>
            {learningData.capabilities && learningData.capabilities.map(cap => (
              <tr key={cap.tag}>
                <td>{cap.tag}</td>
                <td>{cap.weight}</td>
                <td className={cap.change > 0 ? 'positive' : cap.change < 0 ? 'negative' : ''}>
                  {cap.change > 0 ? `+${cap.change}` : cap.change}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AgentLearningViz; 