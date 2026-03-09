import subprocess
import sys
import os

print("正在运行测试...")
os.chdir("c:/Users/11581/Downloads/sport-lottery-sweeper/frontend")

# 尝试运行vitest
result = subprocess.run(
    ["npx", "vitest", "run", "src/tests/unit/test_basic.test.js", "--reporter=verbose", "--no-watch"],
    capture_output=True,
    text=True,
    shell=True
)

print("输出内容:")
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("返回码:", result.returncode)

# 检查是否有输出
if result.stdout:
    if "PASS" in result.stdout or "✓" in result.stdout:
        print("\n✅ 测试通过!")
    elif "FAIL" in result.stdout or "✗" in result.stdout:
        print("\n❌ 测试失败!")
    else:
        print("\n⚠️  没有明确的测试结果")