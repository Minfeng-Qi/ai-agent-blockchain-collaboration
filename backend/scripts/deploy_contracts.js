/**
 * Script to deploy smart contracts for the Agent Learning System
 * 
 * Usage: node deploy_contracts.js
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../.env') });

// Contract artifacts
const AgentRegistryArtifact = require('../contracts/abi/AgentRegistry.json');
const TaskManagerArtifact = require('../contracts/abi/TaskManager.json');
const LearningArtifact = require('../contracts/abi/Learning.json');

// Configuration
const BLOCKCHAIN_RPC_URL = process.env.BLOCKCHAIN_RPC_URL || 'http://localhost:8545';
const PRIVATE_KEY = process.env.DEPLOYER_PRIVATE_KEY; // Add this to .env for production

async function main() {
    console.log('Starting contract deployment...');
    
    // Connect to the blockchain
    let provider;
    let wallet;
    
    try {
        provider = new ethers.providers.JsonRpcProvider(BLOCKCHAIN_RPC_URL);
        
        // Use private key if available, otherwise use default account
        if (PRIVATE_KEY) {
            wallet = new ethers.Wallet(PRIVATE_KEY, provider);
        } else {
            // For development, use the first account from the node
            const accounts = await provider.listAccounts();
            wallet = provider.getSigner(accounts[0]);
            console.log(`Using default account: ${accounts[0]}`);
        }
        
        const network = await provider.getNetwork();
        console.log(`Connected to network: ${network.name} (chainId: ${network.chainId})`);
    } catch (error) {
        console.error('Failed to connect to blockchain:', error);
        process.exit(1);
    }
    
    // Deploy contracts
    const deployedContracts = {};
    
    try {
        // Deploy AgentRegistry
        console.log('Deploying AgentRegistry...');
        const AgentRegistry = new ethers.ContractFactory(
            AgentRegistryArtifact,
            AgentRegistryBytecode,
            wallet
        );
        const agentRegistry = await AgentRegistry.deploy();
        await agentRegistry.deployed();
        deployedContracts.AGENT_REGISTRY_ADDRESS = agentRegistry.address;
        console.log(`AgentRegistry deployed to: ${agentRegistry.address}`);
        
        // Deploy TaskManager
        console.log('Deploying TaskManager...');
        const TaskManager = new ethers.ContractFactory(
            TaskManagerArtifact,
            TaskManagerBytecode,
            wallet
        );
        const taskManager = await TaskManager.deploy(agentRegistry.address);
        await taskManager.deployed();
        deployedContracts.TASK_MANAGER_ADDRESS = taskManager.address;
        console.log(`TaskManager deployed to: ${taskManager.address}`);
        
        // Deploy Learning
        console.log('Deploying Learning...');
        const Learning = new ethers.ContractFactory(
            LearningArtifact,
            LearningBytecode,
            wallet
        );
        const learning = await Learning.deploy(agentRegistry.address);
        await learning.deployed();
        deployedContracts.LEARNING_CONTRACT_ADDRESS = learning.address;
        console.log(`Learning deployed to: ${learning.address}`);
        
    } catch (error) {
        console.error('Error deploying contracts:', error);
        process.exit(1);
    }
    
    // Update .env file with contract addresses
    try {
        const envPath = path.join(__dirname, '../.env');
        let envContent = fs.readFileSync(envPath, 'utf8');
        
        // Update or add contract addresses
        for (const [key, value] of Object.entries(deployedContracts)) {
            const regex = new RegExp(`^${key}=.*$`, 'm');
            if (envContent.match(regex)) {
                envContent = envContent.replace(regex, `${key}=${value}`);
            } else {
                envContent += `\n${key}=${value}`;
            }
        }
        
        fs.writeFileSync(envPath, envContent);
        console.log('Updated .env file with contract addresses');
    } catch (error) {
        console.error('Error updating .env file:', error);
    }
    
    console.log('Contract deployment completed successfully!');
}

// Execute the deployment
main()
    .then(() => process.exit(0))
    .catch(error => {
        console.error(error);
        process.exit(1);
    });