require("@nomicfoundation/hardhat-ethers");
require("@nomicfoundation/hardhat-chai-matchers");
require("dotenv").config();

// 读取环境变量
const PRIVATE_KEY = process.env.PRIVATE_KEY || "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"; // Ganache第一个账户
const INFURA_API_KEY = process.env.INFURA_API_KEY || "";

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      },
      viaIR: false
    }
  },
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545"
    },
    ganache: {
      url: "http://127.0.0.1:8545",
      accounts: [PRIVATE_KEY]
    },
    hardhat: {
      chainId: 1337
    },
    // 如果需要部署到测试网
    sepolia: {
      url: `https://sepolia.infura.io/v3/${INFURA_API_KEY}`,
      accounts: [PRIVATE_KEY]
    }
  },
  paths: {
    sources: "./core",
    tests: "../test-clean",
    artifacts: "../artifacts-clean",
    cache: "../cache-clean"
  }
};
