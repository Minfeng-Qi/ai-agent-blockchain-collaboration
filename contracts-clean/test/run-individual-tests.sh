#!/bin/bash

# 确保使用Node.js v18
if command -v nvm &> /dev/null; then
    nvm use 18
fi

# 函数：运行单个测试
run_test() {
    local test_file=$1
    echo "运行测试: $test_file"
    cd ../contracts-clean && npx hardhat test "../test-clean/$test_file"
    echo "------------------------"
}

# 如果提供了参数，只运行指定的测试
if [ $# -gt 0 ]; then
    for test_file in "$@"; do
        if [ -f "$test_file" ]; then
            run_test "$test_file"
        else
            echo "错误: 测试文件 '$test_file' 不存在"
        fi
    done
    exit 0
fi

# 否则，运行所有测试
echo "运行所有测试..."

for test_file in *.test.js; do
    run_test "$test_file"
done

echo "所有测试完成!"
