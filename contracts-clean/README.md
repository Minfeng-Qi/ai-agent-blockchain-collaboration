# 代理学习系统智能合约

本项目包含代理学习系统的智能合约，这是一个基于区块链的平台，用于管理自主代理、它们的能力以及它们之间的交互。

## 核心合约

系统中的核心合约包括：

- **AgentRegistry**: 管理代理注册、能力和声誉。
- **ActionLogger**: 在链上记录代理操作，以实现透明度和问责制。
- **IncentiveEngine**: 根据代理性能处理声誉更新和能力权重调整。
- **TaskManager**: 管理任务创建、分配和完成。
- **TaskMarketplace**: 促进任务发现和竞标。
- **BidAuction**: 实现任务分配的拍卖机制。
- **MessageHub**: 实现代理之间的可验证消息传递。
- **Learning**: 记录和管理代理学习事件。

## 设置

1. 安装依赖:
   ```
   cd contracts-clean
   npm install
   ```

2. 编译合约:
   ```
   npx hardhat compile
   ```

3. 运行测试:
   ```
   npx hardhat test
   ```

## 项目结构

- `core/`: 包含所有智能合约
- `../test-clean/`: 包含合约的测试文件

## 要求

- Node.js v18+
- npm v10+

## 许可证

MIT
