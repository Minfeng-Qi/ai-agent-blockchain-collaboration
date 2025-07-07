# 项目结构

本文档描述了代理学习系统的项目结构。

## 主要目录

- `contracts-clean/`: 智能合约代码和相关配置
  - `core/`: 核心智能合约
  - `mocks/`: 模拟合约（用于测试）
  - `scripts/`: 部署脚本
- `test-clean/`: 智能合约测试
- `artifacts-clean/`: 编译后的合约工件（自动生成）
- `cache-clean/`: Hardhat缓存（自动生成）

## 核心合约

系统中的核心合约包括：

1. **AgentRegistry.sol**: 管理代理注册、能力和声誉
2. **ActionLogger.sol**: 在链上记录代理操作
3. **IncentiveEngine.sol**: 处理声誉更新和能力权重调整
4. **TaskManager.sol**: 管理任务创建、分配和完成
5. **TaskMarketplace.sol**: 促进任务发现和竞标
6. **BidAuction.sol**: 实现任务分配的拍卖机制
7. **MessageHub.sol**: 实现代理之间的可验证消息传递
8. **Learning.sol**: 记录和管理代理学习事件

## 测试文件

- `minimal.test.js`: 基本功能测试
- `actionlogger.test.js`: ActionLogger合约测试
- `incentiveengine.test.js`: IncentiveEngine合约测试

## 脚本

- `contracts-clean/run-tests.sh`: 运行所有测试的脚本
- `test-clean/run-individual-tests.sh`: 运行单个测试的脚本
- `contracts-clean/scripts/deploy.js`: 部署合约的脚本

## 配置文件

- `contracts-clean/hardhat.config.js`: Hardhat配置
- `contracts-clean/package.json`: 项目依赖

## 开发流程

1. 编写/修改智能合约
2. 编写测试
3. 运行测试验证功能
4. 部署到测试网或主网
