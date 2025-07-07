# Agent Learning System Frontend

A modern React-based frontend for managing blockchain-based agent tasks and learning systems. This application provides a comprehensive interface for monitoring agent performance, task management, and visualizing learning progress.

## Features

- **Modern Dark Theme UI**: Sleek, professional interface with a dark mode design
- **Dashboard**: Real-time overview of system statistics, task status, and agent performance
- **Agent Management**: View and manage agent profiles, capabilities, and learning metrics
- **Task Management**: Create, assign, and monitor tasks across the agent network
- **Learning Visualization**: Track agent learning progress with interactive charts and metrics

## Tech Stack

- **React 18**: Modern UI library for building component-based interfaces
- **Material-UI v5**: Comprehensive UI component library with customizable theming
- **React Router v6**: Declarative routing for React applications
- **Chart.js & Nivo**: Data visualization libraries for creating interactive charts
- **Axios**: Promise-based HTTP client for API requests

## Getting Started

### Prerequisites

- Node.js v14+ and npm/yarn

### Installation

1. Clone the repository
   ```
   git clone <repository-url>
   cd <project-folder>/frontend
   ```

2. Install dependencies
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

3. Start the development server
   ```
   npm start
   ```
   or
   ```
   yarn start
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

```
npm run build
```
or
```
yarn build
```

## Project Structure

```
frontend/
├── public/             # Static files
│   ├── index.html      # HTML template
│   └── manifest.json   # Web app manifest
├── src/                # Source code
│   ├── components/     # React components
│   │   ├── AgentDetails.js
│   │   ├── AgentList.js
│   │   ├── Dashboard.js
│   │   ├── Layout.js
│   │   ├── LearningDashboard.js
│   │   ├── TaskDetails.js
│   │   └── TaskList.js
│   ├── App.js          # Main App component
│   ├── index.js        # Application entry point
│   ├── theme.js        # Material-UI theme configuration
│   └── reportWebVitals.js # Performance metrics
└── package.json        # Project dependencies and scripts
```

## API Integration

The frontend connects to a backend API running at `http://localhost:8000`. The API provides endpoints for:

- Agent management: `/agents`
- Task management: `/tasks`
- Learning metrics: `/learning`
- System statistics: `/stats`

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed: `npm install`
2. Check that the backend API is running at `http://localhost:8000`
3. Clear browser cache and restart the development server

## License

This project is licensed under the MIT License. 