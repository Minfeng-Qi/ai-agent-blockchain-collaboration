#!/bin/bash

# 确保使用Node.js v18
if command -v nvm &> /dev/null; then
    nvm use 18
fi

# 编译合约
echo "编译合约..."
npx hardhat compile

# 运行测试
echo "运行测试..."
npx hardhat test

echo "测试完成!"
