// 部署脚本 (Ethers v6 compatible)
const hre = require("hardhat");

async function main() {
  console.log("开始部署合约...");

  // 部署AgentRegistry
  const AgentRegistry = await hre.ethers.getContractFactory("AgentRegistry");
  const agentRegistry = await AgentRegistry.deploy();
  await agentRegistry.waitForDeployment();
  console.log("AgentRegistry 已部署到:", agentRegistry.target);

  // 部署ActionLogger
  const ActionLogger = await hre.ethers.getContractFactory("ActionLogger");
  const actionLogger = await ActionLogger.deploy(agentRegistry.target);
  await actionLogger.waitForDeployment();
  console.log("ActionLogger 已部署到:", actionLogger.target);

  // 部署IncentiveEngine
  const IncentiveEngine = await hre.ethers.getContractFactory("IncentiveEngine");
  const incentiveEngine = await IncentiveEngine.deploy(agentRegistry.target);
  await incentiveEngine.waitForDeployment();
  console.log("IncentiveEngine 已部署到:", incentiveEngine.target);

  // 设置ActionLogger地址
  await incentiveEngine.setActionLogger(actionLogger.target);
  console.log("IncentiveEngine中设置了ActionLogger地址");

  // 部署TaskManager
  const TaskManager = await hre.ethers.getContractFactory("TaskManager");
  const taskManager = await TaskManager.deploy(agentRegistry.target);
  await taskManager.waitForDeployment();
  console.log("TaskManager 已部署到:", taskManager.target);

  // 部署BidAuction
  const BidAuction = await hre.ethers.getContractFactory("BidAuction");
  const bidAuction = await BidAuction.deploy(agentRegistry.target, taskManager.target);
  await bidAuction.waitForDeployment();
  console.log("BidAuction 已部署到:", bidAuction.target);

  // 设置合约连接
  await taskManager.setBidAuction(bidAuction.target);
  await taskManager.setIncentiveEngine(incentiveEngine.target);
  await bidAuction.setIncentiveEngine(incentiveEngine.target);
  console.log("合约连接已设置");

  // 部署MessageHub
  const MessageHub = await hre.ethers.getContractFactory("MessageHub");
  const messageHub = await MessageHub.deploy(agentRegistry.target);
  await messageHub.waitForDeployment();
  console.log("MessageHub 已部署到:", messageHub.target);

  // 部署Learning
  const Learning = await hre.ethers.getContractFactory("Learning");
  const learning = await Learning.deploy(agentRegistry.target);
  await learning.waitForDeployment();
  console.log("Learning 已部署到:", learning.target);

  // 输出所有合约地址
  console.log("\n📋 合约部署总结:");
  console.log("AgentRegistry:", agentRegistry.target);
  console.log("ActionLogger:", actionLogger.target);
  console.log("IncentiveEngine:", incentiveEngine.target);
  console.log("TaskManager:", taskManager.target);
  console.log("BidAuction:", bidAuction.target);
  console.log("MessageHub:", messageHub.target);
  console.log("Learning:", learning.target);

  console.log("\n✅ 所有合约已成功部署并配置!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
