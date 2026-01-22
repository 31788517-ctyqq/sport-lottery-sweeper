# 项目数据库管理与优化流程报告
**日期**：2026-01-22
**作者**：AI 编程助手（基于实际优化过程总结）

---

## 1. 背景与目标
本项目（竞彩足球扫盘系统）在初期存在数据库结构变更缺乏统一管理、示例数据与结构耦合、环境初始化流程分散等问题。
本次优化的目标：
- 建立 **安全、可重复、自动化** 的数据库管理流程
- 实现 **结构版本化**、**数据与结构分离**、**环境一键初始化**
- 提供 **健康检查** 与 **一键恢复** 能力
- 在 CI 中实现自动化验证，确保每次代码变更不会破坏数据库环境

---

## 2. 优化成果概览
| 领域 | 主要成果 |
|------|----------|
| **结构版本管理** | 使用 Alembic 接管现有 `leagues`、`teams`、`matches` 表，生成初始空迁移 `fd2e6eb3e2ee_initial_structure.py` 并 stamp 版本 |
| **数据与结构分离** | 示例数据移至 `data/seed/sport_lottery_sample_data.sql`，通过 `scripts/seed/seed_runner.py` 防重复导入 |
| **自动初始化** | Windows 环境：`start_backend.bat` 四步流程（迁移→数据→健康检查→启动）<br>Docker 环境：`scripts/docker/entrypoint.sh` 统一入口 |
| **健康监控** | `scripts/health_check/db_health_check.py` 检查 Alembic 版本、表存在性、数据完整性 |
| **一键恢复** | `scripts/recovery/reset_and_recover.py` 删除数据库→重建结构→导入数据→健康检查 |
| **文档化** | README.md 完整覆盖数据库管理、Docker 启动、CI 检查说明 |
| **CI 自动化** | `scripts/ci/db_ci_check.yml` 在 PR/Push 时执行迁移、数据导入、健康检查、测试运行、覆盖率收集 |

---

## 3. 数据库管理流程

### 3.1 结构变更流程
1. **修改模型**  
   在 `backend/models/` 中修改 SQLAlchemy 模型定义。
2. **生成迁移脚本**  
   ```bash
   alembic revision --autogenerate -m "描述"
   ```
3. **检查并编辑脚本**  
   确保迁移逻辑正确（尤其是生产环境不可丢失数据的变更）。
4. **应用迁移**  
   ```bash
   alembic upgrade head
   ```
5. **提交迁移脚本**  
   将生成的版本文件纳入 Git 管理，确保团队同步。

> **严禁** 手动在数据库中增删改表结构，所有变更必须通过 Alembic。

### 3.2 数据初始化流程
- **开发/测试环境**：使用 `seed_runner.py` 导入 `data/seed/sport_lottery_sample_data.sql`，脚本会自动判断表是否为空，避免重复插入。
- **生产环境**：禁用示例数据脚本，使用正式数据导入流程（API 或 ETL）。

### 3.3 环境启动流程
#### 本地 Windows
运行 `start_backend.bat`：
1. `alembic upgrade head`  
2. `python scripts/seed/seed_runner.py`  
3. `python scripts/health_check/db_health_check.py`  
4. `uvicorn backend.main:app`

#### Docker 环境
镜像 ENTRYPOINT 为 `scripts/docker/entrypoint.sh`，执行顺序同上，确保容器启动即完成初始化。

### 3.4 健康检查流程
定期或启动前运行 `db_health_check.py`：
- 检查 Alembic 当前版本  
- 检查 `leagues`、`teams`、`matches` 表是否存在  
- 检查示例数据记录数是否符合预期  

返回码 `0`=健康，`1`=异常，可用于 CI 或启动脚本中断流程。

### 3.5 一键恢复流程
当数据库损坏或结构异常时：
```bash
python scripts/recovery/reset_and_recover.py
```
脚本交互式确认后：
1. 删除 `sport_lottery.db`  
2. 生成新的空迁移并 stamp  
3. 导入种子数据  
4. 执行健康检查  

适用于开发/测试环境快速回滚到干净状态。

---

## 4. 规范与约束
- **版本控制**：所有迁移脚本必须提交到 Git，禁止在服务器手动改库。
- **数据分离**：示例数据仅用于开发/测试，不得进入生产库。
- **环境一致性**：本地、Docker、CI 使用同一套初始化与健康检查流程。
- **异步测试配置**：`pyproject.toml` 必须包含 `asyncio_mode = "auto"`，避免 CI 中异步测试失败。
- **权限控制**：生产环境数据库账号应限制 DDL 权限，只允许 Alembic 迁移用户执行结构变更。

---

## 5. 工具链与文件结构
```
data/seed/sport_lottery_sample_data.sql   # 示例数据
scripts/seed/seed_runner.py               # 防重复数据导入
scripts/health_check/db_health_check.py   # 健康检查
scripts/recovery/reset_and_recover.py     # 一键恢复
scripts/docker/entrypoint.sh              # Docker 启动入口
scripts/ci/db_ci_check.yml                # GitHub Actions CI 检查
alembic/versions/                         # Alembic 迁移脚本
alembic.ini                               # Alembic 配置
start_backend.bat                         # Windows 启动入口
README.md                                 # 文档说明
```

---

## 6. CI/CD 集成
- **触发条件**：`push` 到 `main`/`develop`，或 PR 到 `main`  
- **执行内容**：依赖安装 → 补全 pytest 配置 → Alembic 迁移 → 数据导入 → 健康检查 → pytest 测试 → 覆盖率上传  
- **优势**：提前捕获数据库结构、数据、测试问题，防止破坏主分支稳定性。

---

## 7. 后续演进建议
1. **升级到 PostgreSQL**  
   SQLite 适合轻量开发，生产多并发场景建议迁移至 PostgreSQL，修改 `alembic.ini` 与 Docker 配置即可。
2. **完善测试体系**  
   按 `TEST_MODULES_HEALTH_REPORT.md` 建议，补齐集成测试与 E2E 测试，统一数据库配置。
3. **多环境管理**  
   使用 `.env` 或配置中心管理不同环境的数据库连接，避免硬编码。
4. **迁移回滚策略**  
   为关键迁移编写 `downgrade` 逻辑，确保可安全回滚。
5. **监控与告警**  
   在 CI 或生产环境加入数据库健康检查定时任务，异常时触发告警。

---

## 8. 总结
本次优化建立了从 **结构版本化 → 数据初始化 → 自动启动 → 健康检查 → 一键恢复 → CI 验证** 的完整数据库生命周期管理体系，兼顾开发效率与生产安全性。  
只要遵循本流程与规范，团队的数据库管理将具备高度可重复性、可追溯性和安全性，为后续功能迭代与规模扩展奠定坚实基础。