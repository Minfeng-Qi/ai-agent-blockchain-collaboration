import React from 'react';

function StatsPanel({ stats }) {
  return (
    <div className="stats-panel">
      <h2>System Statistics</h2>
      <div className="stats-grid">
        <div className="stat-item">
          <span className="stat-label">Total Tasks</span>
          <span className="stat-value">{stats.total || 0}</span>
        </div>
        
        <div className="stat-item">
          <span className="stat-label">Available</span>
          <span className="stat-value available">{stats.available || 0}</span>
        </div>
        
        <div className="stat-item">
          <span className="stat-label">Assigned</span>
          <span className="stat-value assigned">{stats.assigned || 0}</span>
        </div>
        
        <div className="stat-item">
          <span className="stat-label">Completed</span>
          <span className="stat-value completed">{stats.completed || 0}</span>
        </div>
        
        <div className="stat-item">
          <span className="stat-label">Failed</span>
          <span className="stat-value failed">{stats.failed || 0}</span>
        </div>
      </div>
    </div>
  );
}

export default StatsPanel;