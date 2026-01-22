@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════╗
echo ║   命名规则优化 - 总控制台                     ║
echo ║   Sport Lottery Sweeper                        ║
echo ╚════════════════════════════════════════════════╝
echo.

cd /d %~dp0..

:menu
echo.
echo ══════════════════════════════════════════════════
echo  请选择要执行的阶段：
echo ══════════════════════════════════════════════════
echo.
echo  [0] 🔍 查看优化计划（文档）
echo  [1] 🗂️  Phase 1: 清理文件结构
echo  [2] 🏷️  Phase 2: 枚举类命名统一（暂未实现）
echo  [3] 🌐 Phase 3: API 路由国际化（暂未实现）
echo  [4] 🎨 Phase 4: CSS 类名规范化（暂未实现）
echo  [5] 📊 Phase 5: 常量命名优化（暂未实现）
echo.
echo  [V] ✅ 验证 Phase 1
echo  [R] ⏮️  回滚 Phase 1
echo.
echo  [H] 📚 查看帮助
echo  [Q] 🚪 退出
echo.
echo ══════════════════════════════════════════════════
echo.

set /p choice="请输入选项: "

if /i "%choice%"=="0" goto view_docs
if /i "%choice%"=="1" goto phase1
if /i "%choice%"=="V" goto verify
if /i "%choice%"=="R" goto rollback
if /i "%choice%"=="H" goto help
if /i "%choice%"=="Q" goto quit

echo.
echo [错误] 无效的选项！
timeout /t 2 >nul
goto menu

:view_docs
cls
echo ══════════════════════════════════════════════════
echo  📚 查看优化计划文档
echo ══════════════════════════════════════════════════
echo.
if exist "docs\NAMING_OPTIMIZATION_PLAN.md" (
    echo 正在打开文档...
    start "" "docs\NAMING_OPTIMIZATION_PLAN.md"
    timeout /t 1 >nul
) else (
    echo [错误] 未找到文档文件
)
goto menu

:phase1
cls
echo ══════════════════════════════════════════════════
echo  🗂️  Phase 1: 清理文件结构
echo ══════════════════════════════════════════════════
echo.
echo 此阶段将执行：
echo   1. 清理 Backend 临时文件
echo   2. 修复前端目录结构
echo   3. 整理根目录文档
echo.
echo 风险等级: 🟢 低
echo 预计时间: 2-4 小时
echo 可回滚: ✅ 是
echo.
choice /c YN /m "确认执行 Phase 1"

if errorlevel 2 goto menu

echo.
echo ─────────────────────────────────────────────────
echo  步骤 1/3: 清理 Backend
echo ─────────────────────────────────────────────────
call scripts\phase1-cleanup-backend.bat
echo.

echo.
echo ─────────────────────────────────────────────────
echo  步骤 2/3: 修复前端结构
echo ─────────────────────────────────────────────────
call scripts\phase1-fix-frontend-structure.bat
echo.

echo.
echo ─────────────────────────────────────────────────
echo  步骤 3/3: 验证结果
echo ─────────────────────────────────────────────────
call scripts\verify-phase1.bat
echo.

echo.
echo ══════════════════════════════════════════════════
echo ✅ Phase 1 执行完成！
echo ══════════════════════════════════════════════════
echo.
echo 下一步建议：
echo 1. 运行完整测试: pytest backend/tests/
echo 2. 启动后端验证: python backend/main.py
echo 3. 启动前端验证: npm run dev
echo 4. 如一切正常，提交代码: git add . ^&^& git commit -m "refactor: Phase 1 文件结构优化"
echo.
pause
goto menu

:verify
cls
echo ══════════════════════════════════════════════════
echo  ✅ 验证 Phase 1
echo ══════════════════════════════════════════════════
call scripts\verify-phase1.bat
goto menu

:rollback
cls
echo ══════════════════════════════════════════════════
echo  ⏮️  回滚 Phase 1
echo ══════════════════════════════════════════════════
call scripts\rollback-phase1.bat
goto menu

:help
cls
echo ══════════════════════════════════════════════════
echo  📚 帮助信息
echo ══════════════════════════════════════════════════
echo.
echo 🎯 优化目标
echo    - 提升项目结构清晰度 100%%
echo    - 提升命名一致性 32%%
echo    - 提升代码可维护性 38%%
echo    - 确保系统零宕机
echo.
echo 📋 优化阶段
echo    Phase 0: 准备阶段（Git 分支、备份）
echo    Phase 1: 文件结构优化 ⭐ 当前可执行
echo    Phase 2: 枚举类命名统一
echo    Phase 3: API 路由国际化
echo    Phase 4: CSS 类名规范化
echo    Phase 5: 常量命名优化
echo.
echo 🔒 安全机制
echo    ✅ 每步都有备份
echo    ✅ 支持快速回滚
echo    ✅ 验证脚本确保完整性
echo    ✅ 分阶段执行，降低风险
echo.
echo 📖 详细文档
echo    - 优化计划: docs\NAMING_OPTIMIZATION_PLAN.md
echo    - 健康检查: docs\NAMING_CONVENTION_HEALTH_CHECK.md
echo    - 业务模块: docs\BUSINESS_MODULES_OVERVIEW.md
echo.
echo 🆘 遇到问题
echo    1. 查看 .naming-optimization\ 目录中的日志
echo    2. 使用回滚脚本恢复
echo    3. 查阅文档中的故障排查部分
echo.
pause
goto menu

:quit
cls
echo.
echo ╔════════════════════════════════════════════════╗
echo ║   感谢使用命名规则优化工具                     ║
echo ║   Good luck! 🚀                                ║
echo ╚════════════════════════════════════════════════╝
echo.
timeout /t 2 >nul
exit /b 0
