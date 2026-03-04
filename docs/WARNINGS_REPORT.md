# Warnings 报告（未完成工作）

状态：未完成（待处理）

生成时间：2026-02-27

来源：`pytest` 全量测试输出（65 passed, 101 warnings）

## 摘要
当前 warnings 主要为开发/测试期弃用与测试规范提醒，不是生产运行时错误。

## 主要类型与示例

### 1) Pydantic v2 弃用提示
- 说明：仍在使用 v1 风格 `@validator` / `dict()` / `from_orm()`。
- 示例：
  - `backend/schemas/admin_user.py` 中 `@validator`
  - `backend/api/v1/users.py` 中 `user_update.dict()` / `UserResponse.from_orm()`

### 2) SQLAlchemy 2.0 弃用提示
- 说明：`declarative_base()` 与部分旧式 mapper API 已弃用。
- 示例：
  - `backend/database.py`：`declarative_base()`
  - `backend/models/data_review.py`：`sqlalchemy.orm.mapper()` 事件
  - `backend/models/multi_strategy.py`：`declarative_base()`

### 3) Pytest 规范警告
- 说明：测试用例不应 `return` 值。
- 示例：
  - `tests/unit/test_auth_direct.py::test_auth_login_direct` 返回了 `int`

### 4) SQLAlchemy drop_all 外键依赖告警
- 说明：`drop_all` 因 FK 环依赖导致排序失败（SQLite 不支持 ALTER）。
- 示例：
  - `tests/test_user_management.py` teardown
  - `tests/test_user_activity_logger.py` teardown

## 未完成工作（待处理清单）
1. 替换 Pydantic v1 风格 `@validator` 为 `@field_validator`。
2. 将 `dict()` 替换为 `model_dump()`；`from_orm()` 替换为 `model_validate()`。
3. 迁移 SQLAlchemy 旧式 `declarative_base()` 与 `mapper()` 用法。
4. 修复 `tests/unit/test_auth_direct.py` 中不应 `return` 的测试函数。
5. 处理 `drop_all` 的外键环依赖（例如 `use_alter=True` 或拆分清理顺序）。

## 备注
本报告记录 warnings，未做清理。后续若需要，我可以逐项修复并重新生成报告。
