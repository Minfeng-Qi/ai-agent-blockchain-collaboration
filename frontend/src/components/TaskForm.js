import React, { useState } from 'react';

function TaskForm({ onSubmit }) {
  const [description, setDescription] = useState('');
  const [requirements, setRequirements] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Prepare task data
    const taskData = {
      description: description,
      requirements: requirements.split(',').map(req => req.trim()).filter(req => req !== '')
    };
    
    onSubmit(taskData);
    
    // Reset form
    setDescription('');
    setRequirements('');
  };
  
  return (
    <div className="task-form">
      <h2>Create New Task</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="description">Task Description:</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            rows={4}
            placeholder="Describe the task in detail..."
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="requirements">Requirements (comma-separated):</label>
          <input
            type="text"
            id="requirements"
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            placeholder="e.g., code_generation, text_analysis, data_processing"
          />
        </div>
        
        <button type="submit" className="submit-button">Submit Task</button>
      </form>
    </div>
  );
}

export default TaskForm;