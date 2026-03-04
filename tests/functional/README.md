# 功能测试目录说明

## 目录结构
- archived/: 已废弃或过时的测试文件
- debug_tools/: 开发和调试用的工具脚本  
- maintenance/: 测试环境维护和执行的脚本
- validation/: 验证工具

## 使用说明
- 日常开发请使用 tests/unit/ 和 tests/integration/
- 调试工具请在必要时使用，不建议在CI中执行
- 维护脚本可用于本地环境设置和测试执行
