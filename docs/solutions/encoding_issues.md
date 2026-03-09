# AI_WORKING: coder1 @1769627946 - 创建编码问题解决方案

# 编码问题（UTF-8）

## 症状描述
- Python 文件出现 `SyntaxError: invalid non-printable character U+E103` 等错误
- JavaScript/Vue 文件中文显示乱码
- 批处理脚本执行时输出乱码
- 文件保存后再次打开出现编码警告

## 根本原因
项目要求所有 Python 和 JavaScript 文件使用 UTF-8 编码，但有时编辑器默认使用系统编码（如 Windows 的 GBK）导致问题。

## 解决方案

### 1. 检查文件编码
```bash
# 使用 file 命令（Linux/macOS）
file backend/models/user.py

# Windows 下可使用 PowerShell
Get-Content backend/models/user.py -Encoding Byte | Select-Object -First 100
```

### 2. 转换文件编码为 UTF-8
```bash
# 使用 iconv（Linux/macOS）
iconv -f GBK -t UTF-8 backend/models/user.py > backend/models/user_utf8.py
mv backend/models/user_utf8.py backend/models/user.py

# Windows 下可使用 PowerShell
Get-Content backend/models/user.py -Encoding Default | Out-File -Encoding UTF8 backend/models/user_utf8.py
Move-Item backend/models/user_utf8.py backend/models/user.py -Force
```

### 3. 配置编辑器使用 UTF-8
**VS Code**：
1. 文件 → 首选项 → 设置
2. 搜索 "files.encoding"
3. 设置为 "utf8"
4. 勾选 "files.autoGuessEncoding"

**PyCharm**：
1. File → Settings → Editor → File Encodings
2. 设置 Global Encoding、Project Encoding 为 UTF-8
3. 勾选 "Transparent native-to-ascii conversion"

### 4. 添加编码声明
在 Python 文件开头添加：
```python
# -*- coding: utf-8 -*-
```

在 JavaScript/Vue 文件开头添加：
```javascript
// @charset "UTF-8";
```

### 5. 验证编码
```python
# Python 脚本验证
import chardet
with open('backend/models/user.py', 'rb') as f:
    result = chardet.detect(f.read())
    print(f"检测到的编码: {result['encoding']}")
```

## 预防措施
- 项目规范要求所有源代码文件使用 UTF-8 编码
- 新创建文件时确保编辑器设置为 UTF-8
- 版本控制系统中统一文件编码
- 在项目根目录添加 `.editorconfig` 文件统一编码设置

## 相关文档
- [项目编码规范](../PROJECT_STANDARDS.md)
- [前端文件结构规则](../../.codebuddy/rules/frontend-file-structure.mdc)

# AI_DONE: coder1 @1769627946