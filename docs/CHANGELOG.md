# Changelog

## [1.1.0] - 2023-06-15

### Added
- Comprehensive integration tests for the enhanced capability and workload management system
- Unit tests for the IncentiveEngine contract
- Test README with detailed instructions for running tests
- Script for managing Node.js version compatibility

### Enhanced
- AgentRegistry now supports capability management and workload tracking
- IncentiveEngine implements tag-specific capability scoring
- BidAuction calculates utility based on capabilities, workload, and task requirements
- TaskManager supports capability-based task evaluation

### Fixed
- Node.js version compatibility issues with Hardhat
- Integration between contracts for capability and workload management

## [1.0.0] - 2023-05-30

### Added
- Initial implementation of the blockchain-based LLM multi-agent coordination system
- Six core smart contracts: AgentRegistry, MessageHub, TaskManager, BidAuction, ActionLogger, and IncentiveEngine
- Basic agent registration and authentication
- Task creation, bidding, and assignment workflow
- Reputation management system
- Message passing with signature verification
- Action logging for audit trails 