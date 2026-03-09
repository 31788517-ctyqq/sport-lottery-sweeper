# 数据库使用说明文档

## 📚 目录

1. [快速开始](#快速开始)
2. [数据库配置](#数据库配置)
3. [模型使用指南](#模型使用指南)
4. [常用查询示例](#常用查询示例)
5. [数据迁移](#数据迁移)
6. [性能优化](#性能优化)
7. [故障排查](#故障排查)
8. [最佳实践](#最佳实践)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 主要依赖包：
# - sqlalchemy >= 2.0.0
# - alembic >= 1.12.0
# - psycopg2-binary >= 2.9.0 (PostgreSQL)
# - aiosqlite >= 0.19.0 (SQLite异步支持)
```

### 2. 配置数据库连接

编辑 `.env` 文件：

```env
# 开发环境 (SQLite)
DATABASE_URL=sqlite:///./sport_lottery.db
ASYNC_DATABASE_URL=sqlite+aiosqlite:///./sport_lottery.db

# 生产环境 (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/sport_lottery_db
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sport_lottery_db
```

### 3. 初始化数据库

```bash
# 创建数据库表
python -c "from backend.database import engine; from backend.models.base import Base; Base.metadata.create_all(engine)"

# 或使用Alembic迁移
alembic upgrade head
```

### 4. 验证安装

```python
from backend.database import SessionLocal
from backend.models import Match, League, Team

# 创建数据库会话
db = SessionLocal()

# 测试查询
leagues = db.query(League).all()
print(f"找到 {len(leagues)} 个联赛")

db.close()
```

---

## ⚙️ 数据库配置

### 配置文件位置

| 环境 | 配置文件 | 说明 |
|-----|---------|------|
| 开发 | `.env` | 本地开发配置 |
| 测试 | `.env.test` | 测试环境配置 |
| 生产 | `config/production/backend.env` | 生产环境配置 |

### 连接池配置

```python
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    DATABASE_URL,
    
    # 连接池配置
    pool_size=20,              # 连接池大小
    max_overflow=10,           # 最大溢出连接数
    pool_timeout=30,           # 连接超时(秒)
    pool_recycle=3600,         # 连接回收时间(秒)
    pool_pre_ping=True,        # 连接前检查有效性
    
    # 其他配置
    echo=False,                # 是否打印SQL
    echo_pool=False,           # 是否打印连接池日志
    connect_args={
        "check_same_thread": False  # SQLite特定
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
```

### 异步数据库配置

```python
# backend/core/async_database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10
)

async_session = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

---

## 📖 模型使用指南

### 1. 基础模型类

所有模型都继承自基础类，提供通用功能：

```python
from backend.models.base import (
    Base,              # 基础类
    BaseModel,         # 带时间戳
    BaseAuditModel,    # 带审计信息
    BaseSoftDeleteModel, # 带软删除
    BaseFullModel      # 完整功能
)

# 示例：创建新模型
class MyModel(BaseFullModel):
    __tablename__ = "my_table"
    
    name = Column(String(100), nullable=False)
    value = Column(Integer, default=0)
```

### 2. 导入模型

```python
# 导入所有模型
from backend.models import (
    # 比赛相关
    Match, Team, League, Venue, Player,
    MatchLineup, MatchEvent,
    
    # 情报相关
    Intelligence, IntelligenceType, IntelligenceSource,
    IntelligenceRelation, IntelligenceAnalytics,
    
    # 用户相关
    User, Role, Permission,
    UserLoginLog, UserActivity, UserSubscription,
    
    # 赔率相关
    Odds, OddsMovement, Bookmaker, OddsProvider,
    
    # 预测相关
    Prediction, UserPrediction,
    
    # 管理相关
    DataReview, ValidationRule, ValidationError,
    
    # 枚举类型
    MatchStatusEnum, UserRole, OddsType,
    IntelligenceTypeEnum, PredictionMethod,
)
```

### 3. 创建数据

```python
from backend.database import SessionLocal
from backend.models import League, Team, Match
from datetime import datetime, timedelta

db = SessionLocal()

# 方法1: 直接创建
try:
    # 创建联赛
    league = League(
        name="英格兰超级联赛",
        code="premier_league",
        country="英格兰",
        country_code="ENG",
        level=1,
        is_popular=True
    )
    db.add(league)
    db.commit()
    db.refresh(league)  # 刷新获取ID
    
    # 创建球队
    team1 = Team(
        name="曼彻斯特联队",
        code="MAN_UTD",
        country="英格兰",
        country_code="ENG",
        league_id=league.id
    )
    
    team2 = Team(
        name="利物浦",
        code="LIV",
        country="英格兰",
        country_code="ENG",
        league_id=league.id
    )
    
    db.add_all([team1, team2])
    db.commit()
    
    # 创建比赛
    match = Match(
        match_identifier="EPL_2026_001",
        home_team_id=team1.id,
        away_team_id=team2.id,
        league_id=league.id,
        match_date=datetime.now().date(),
        scheduled_kickoff=datetime.now() + timedelta(days=1),
        status=MatchStatusEnum.SCHEDULED,
        importance=MatchImportanceEnum.HIGH
    )
    
    db.add(match)
    db.commit()
    
    print(f"创建比赛成功: {match.id}")
    
except Exception as e:
    db.rollback()
    print(f"创建失败: {e}")
finally:
    db.close()
```

### 4. 查询数据

```python
# 简单查询
matches = db.query(Match).all()

# 条件查询
active_matches = db.query(Match).filter(
    Match.status == MatchStatusEnum.SCHEDULED
).all()

# 关联查询
matches_with_teams = db.query(Match)\
    .join(Match.home_team)\
    .join(Match.away_team)\
    .filter(Match.league_id == 1)\
    .all()

# 聚合查询
from sqlalchemy import func

match_count = db.query(func.count(Match.id))\
    .filter(Match.status == MatchStatusEnum.FINISHED)\
    .scalar()

# 分页查询
page = 1
page_size = 10
offset = (page - 1) * page_size

matches = db.query(Match)\
    .order_by(Match.scheduled_kickoff.desc())\
    .offset(offset)\
    .limit(page_size)\
    .all()
```

### 5. 更新数据

```python
# 方法1: 直接修改对象
match = db.query(Match).get(1)
match.status = MatchStatusEnum.LIVE
match.home_score = 1
match.away_score = 0
db.commit()

# 方法2: 使用update方法
match.update(
    status=MatchStatusEnum.FINISHED,
    home_score=2,
    away_score=1
)
db.commit()

# 方法3: 批量更新
db.query(Match)\
    .filter(Match.league_id == 1)\
    .update({Match.popularity: Match.popularity + 1})
db.commit()
```

### 6. 删除数据

```python
# 软删除 (推荐)
match = db.query(Match).get(1)
match.soft_delete()
db.commit()

# 恢复软删除
match.restore()
db.commit()

# 硬删除
db.delete(match)
db.commit()

# 批量删除
db.query(Match)\
    .filter(Match.is_deleted == True)\
    .delete()
db.commit()
```

---

## 🔍 常用查询示例

### 1. 比赛查询

```python
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

# 获取今日比赛
today = datetime.now().date()
today_matches = db.query(Match)\
    .filter(Match.match_date == today)\
    .all()

# 获取未来3天的比赛
future_matches = db.query(Match)\
    .filter(
        and_(
            Match.match_date >= today,
            Match.match_date <= today + timedelta(days=3)
        )
    )\
    .order_by(Match.scheduled_kickoff)\
    .all()

# 获取热门比赛
hot_matches = db.query(Match)\
    .filter(Match.popularity > 80)\
    .order_by(Match.popularity.desc())\
    .limit(10)\
    .all()

# 获取联赛比赛 (带球队信息)
matches_with_info = db.query(Match)\
    .join(Match.league)\
    .join(Match.home_team)\
    .join(Match.away_team)\
    .filter(League.code == "premier_league")\
    .all()

# 访问关联数据
for match in matches_with_info:
    print(f"{match.home_team.name} vs {match.away_team.name}")
    print(f"联赛: {match.league.name}")
    print(f"时间: {match.scheduled_kickoff}")
```

### 2. 情报查询

```python
# 获取比赛情报
intelligence_list = db.query(Intelligence)\
    .filter(Intelligence.match_id == 1)\
    .order_by(Intelligence.calculated_weight.desc())\
    .all()

# 获取高权重情报
high_weight_intel = db.query(Intelligence)\
    .filter(
        and_(
            Intelligence.calculated_weight > 0.7,
            Intelligence.is_verified == True
        )
    )\
    .all()

# 按类型查询情报
from backend.models import IntelligenceTypeEnum

injury_intel = db.query(Intelligence)\
    .join(Intelligence.type_info)\
    .filter(IntelligenceType.code == "injury")\
    .all()

# 按来源查询情报
official_intel = db.query(Intelligence)\
    .join(Intelligence.source_info)\
    .filter(IntelligenceSource.is_official == True)\
    .all()

# 全文搜索 (使用LIKE)
keyword = "伤病"
search_results = db.query(Intelligence)\
    .filter(
        or_(
            Intelligence.title.like(f"%{keyword}%"),
            Intelligence.content.like(f"%{keyword}%")
        )
    )\
    .all()
```

### 3. 用户查询

```python
# 获取活跃用户
active_users = db.query(User)\
    .filter(User.status == UserStatus.ACTIVE)\
    .order_by(User.login_count.desc())\
    .limit(100)\
    .all()

# 获取用户及其角色
user_with_roles = db.query(User)\
    .join(User.roles)\
    .filter(User.id == 1)\
    .first()

print(f"用户角色: {[role.name for role in user_with_roles.roles]}")

# 获取用户预测统计
from sqlalchemy import func

user_prediction_stats = db.query(
    User.username,
    func.count(UserPrediction.id).label('total_predictions'),
    func.sum(UserPrediction.profit_loss).label('total_profit')
)\
    .join(UserPrediction)\
    .group_by(User.id)\
    .order_by(func.sum(UserPrediction.profit_loss).desc())\
    .limit(10)\
    .all()

for username, count, profit in user_prediction_stats:
    print(f"{username}: {count}次预测, 盈亏: {profit}")
```

### 4. 赔率查询

```python
# 获取比赛赔率
odds_list = db.query(Odds)\
    .filter(Odds.match_id == 1)\
    .order_by(Odds.last_updated.desc())\
    .all()

# 获取最新赔率
latest_odds = db.query(Odds)\
    .filter(Odds.match_id == 1)\
    .order_by(Odds.last_updated.desc())\
    .first()

# 获取赔率变动历史
odds_movements = db.query(OddsMovement)\
    .join(OddsMovement.odds)\
    .filter(Odds.match_id == 1)\
    .order_by(OddsMovement.movement_time)\
    .all()

# 比较不同博彩商赔率
odds_comparison = db.query(Odds)\
    .join(Odds.bookmaker)\
    .filter(
        and_(
            Odds.match_id == 1,
            Odds.odds_type == OddsType.WIN_DRAW_LOSS
        )
    )\
    .all()

for odds in odds_comparison:
    print(f"{odds.bookmaker.name}: {odds.home_win_odds} / {odds.draw_odds} / {odds.away_win_odds}")
```

### 5. 统计查询

```python
# 联赛比赛统计
league_stats = db.query(
    League.name,
    func.count(Match.id).label('total_matches'),
    func.avg(Match.popularity).label('avg_popularity')
)\
    .join(Match)\
    .group_by(League.id)\
    .order_by(func.count(Match.id).desc())\
    .all()

# 球队胜率统计
team_stats = db.query(
    Team.name,
    func.count(Match.id).label('total_matches'),
    func.sum(
        (Match.home_team_id == Team.id) & (Match.home_score > Match.away_score)
    ).label('home_wins'),
    func.sum(
        (Match.away_team_id == Team.id) & (Match.away_score > Match.home_score)
    ).label('away_wins')
)\
    .join(Match, or_(
        Match.home_team_id == Team.id,
        Match.away_team_id == Team.id
    ))\
    .filter(Match.status == MatchStatusEnum.FINISHED)\
    .group_by(Team.id)\
    .all()

# 情报类型统计
intelligence_type_stats = db.query(
    IntelligenceType.name,
    func.count(Intelligence.id).label('count'),
    func.avg(Intelligence.calculated_weight).label('avg_weight')
)\
    .join(Intelligence)\
    .group_by(IntelligenceType.id)\
    .order_by(func.count(Intelligence.id).desc())\
    .all()
```

---

## 🔄 数据迁移

### 使用Alembic管理数据库迁移

#### 1. 初始化Alembic

```bash
# 已经初始化，配置在 alembic.ini 和 alembic/env.py
```

#### 2. 创建迁移脚本

```bash
# 自动生成迁移脚本
alembic revision --autogenerate -m "Add new column to matches table"

# 手动创建迁移脚本
alembic revision -m "Manual migration"
```

#### 3. 编辑迁移脚本

```python
# alembic/versions/xxx_add_new_column.py

from alembic import op
import sqlalchemy as sa

def upgrade():
    # 添加列
    op.add_column('matches', sa.Column('new_field', sa.String(50), nullable=True))
    
    # 创建索引
    op.create_index('idx_matches_new_field', 'matches', ['new_field'])
    
    # 修改列
    op.alter_column('matches', 'old_field', new_column_name='renamed_field')

def downgrade():
    # 回滚操作
    op.drop_index('idx_matches_new_field', 'matches')
    op.drop_column('matches', 'new_field')
```

#### 4. 应用迁移

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade <revision_id>

# 回滚一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade <revision_id>
```

#### 5. 常用迁移操作

```python
# 添加表
op.create_table(
    'new_table',
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('name', sa.String(100), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
)

# 删除表
op.drop_table('old_table')

# 添加外键
op.create_foreign_key(
    'fk_matches_league',
    'matches', 'leagues',
    ['league_id'], ['id'],
    ondelete='CASCADE'
)

# 删除外键
op.drop_constraint('fk_matches_league', 'matches', type_='foreignkey')

# 批量数据迁移
from sqlalchemy.sql import table, column

matches_table = table('matches',
    column('id', sa.Integer),
    column('status', sa.String)
)

op.execute(
    matches_table.update()
    .where(matches_table.c.status == 'old_status')
    .values(status='new_status')
)
```

---

## ⚡ 性能优化

### 1. 查询优化

```python
# ❌ N+1查询问题
matches = db.query(Match).all()
for match in matches:
    print(match.home_team.name)  # 每次循环都查询数据库

# ✅ 使用joinedload预加载
from sqlalchemy.orm import joinedload

matches = db.query(Match)\
    .options(
        joinedload(Match.home_team),
        joinedload(Match.away_team),
        joinedload(Match.league)
    )\
    .all()

for match in matches:
    print(match.home_team.name)  # 不会触发额外查询
```

### 2. 批量操作

```python
# ❌ 逐条插入
for data in match_data:
    match = Match(**data)
    db.add(match)
    db.commit()

# ✅ 批量插入
db.bulk_insert_mappings(Match, match_data)
db.commit()

# ✅ 批量更新
updates = [
    {'id': 1, 'popularity': 80},
    {'id': 2, 'popularity': 90}
]
db.bulk_update_mappings(Match, updates)
db.commit()
```

### 3. 使用索引

```python
# 为常用查询字段创建索引
from sqlalchemy import Index

# 单列索引
idx_match_date = Index('idx_matches_match_date', Match.match_date)

# 组合索引
idx_status_date = Index('idx_matches_status_date', 
                        Match.status, Match.match_date)

# 部分索引 (PostgreSQL)
idx_active_matches = Index('idx_matches_active',
                           Match.match_date,
                           postgresql_where=(Match.status == 'scheduled'))
```

### 4. 使用查询缓存

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_popular_leagues():
    db = SessionLocal()
    try:
        leagues = db.query(League)\
            .filter(League.is_popular == True)\
            .all()
        return [league.to_dict() for league in leagues]
    finally:
        db.close()
```

### 5. 使用物化视图

```sql
-- 创建物化视图
CREATE MATERIALIZED VIEW match_statistics AS
SELECT 
    league_id,
    COUNT(*) as total_matches,
    AVG(popularity) as avg_popularity,
    COUNT(CASE WHEN status = 'finished' THEN 1 END) as finished_matches
FROM matches
GROUP BY league_id;

-- 创建索引
CREATE INDEX idx_match_stats_league ON match_statistics(league_id);

-- 刷新物化视图
REFRESH MATERIALIZED VIEW match_statistics;
```

---

## 🔧 故障排查

### 常见问题

#### 1. 连接池耗尽

**症状**: `QueuePool limit of size X overflow Y reached`

**解决方案**:
```python
# 增加连接池大小
engine = create_engine(
    DATABASE_URL,
    pool_size=30,        # 增加到30
    max_overflow=20      # 增加到20
)

# 确保正确关闭连接
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
```

#### 2. 死锁问题

**症状**: `deadlock detected`

**解决方案**:
```python
# 使用统一的锁定顺序
with db.begin():
    # 按ID排序锁定，避免死锁
    matches = db.query(Match)\
        .filter(Match.id.in_([1, 2, 3]))\
        .order_by(Match.id)\
        .with_for_update()\
        .all()
    
    for match in matches:
        match.popularity += 1
```

#### 3. 内存泄漏

**症状**: 内存占用持续增长

**解决方案**:
```python
# 使用 expunge_all 清理会话
db.expunge_all()

# 或使用 close 关闭会话
db.close()

# 大批量查询使用 yield_per
for match in db.query(Match).yield_per(100):
    process(match)
    db.expunge(match)  # 及时释放对象
```

#### 4. 查询超时

**症状**: `OperationalError: (psycopg2.OperationalError) FATAL: terminating connection due to statement timeout`

**解决方案**:
```python
# 设置查询超时
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_timeout(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("SET statement_timeout = 30000")  # 30秒
    cursor.close()

# 或使用上下文管理器
with db.execution_options(timeout=30):
    results = db.query(Match).all()
```

### 调试技巧

```python
# 打印SQL语句
from sqlalchemy import event

@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    print("SQL:", statement)
    print("参数:", params)

# 启用SQLAlchemy日志
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 查看查询计划 (PostgreSQL)
from sqlalchemy import text

query = db.query(Match).filter(Match.league_id == 1)
plan = db.execute(text(f"EXPLAIN ANALYZE {query}"))
print(plan.fetchall())
```

---

## 💡 最佳实践

### 1. 会话管理

```python
# ✅ 使用依赖注入
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/matches")
async def get_matches(db: Session = Depends(get_db)):
    return db.query(Match).all()
```

### 2. 事务管理

```python
# ✅ 使用上下文管理器
from contextlib import contextmanager

@contextmanager
def transaction():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

# 使用
with transaction() as db:
    match = Match(...)
    db.add(match)
    # 自动commit或rollback
```

### 3. 模型设计

```python
# ✅ 使用混入类
class MyModel(BaseFullModel):
    # 自动包含: id, created_at, updated_at, is_deleted, deleted_at,
    #           created_by, updated_by, deleted_by
    pass

# ✅ 定义属性方法
class Match(BaseFullModel):
    @property
    def is_finished(self) -> bool:
        return self.status == MatchStatusEnum.FINISHED
    
    @property
    def result_summary(self) -> str:
        if not self.is_finished:
            return "未开始"
        return f"{self.home_score}-{self.away_score}"
```

### 4. 数据验证

```python
# ✅ 使用Pydantic模型
from pydantic import BaseModel, validator

class MatchCreate(BaseModel):
    match_identifier: str
    home_team_id: int
    away_team_id: int
    
    @validator('home_team_id', 'away_team_id')
    def team_id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('球队ID必须为正数')
        return v
    
    @validator('away_team_id')
    def teams_must_be_different(cls, v, values):
        if 'home_team_id' in values and v == values['home_team_id']:
            raise ValueError('主客队不能相同')
        return v
```

### 5. 错误处理

```python
# ✅ 捕获特定异常
from sqlalchemy.exc import IntegrityError, DataError

try:
    db.add(match)
    db.commit()
except IntegrityError:
    db.rollback()
    raise HTTPException(status_code=400, detail="数据重复或违反约束")
except DataError:
    db.rollback()
    raise HTTPException(status_code=400, detail="数据类型错误")
```

### 6. 分页查询

```python
# ✅ 创建分页工具函数
def paginate(query, page: int, page_size: int):
    total = query.count()
    items = query.offset((page - 1) * page_size)\
                 .limit(page_size)\
                 .all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }

# 使用
result = paginate(db.query(Match), page=1, page_size=10)
```

---

## 📞 支持和反馈

### 获取帮助

- **文档**: 查看项目README和其他文档
- **Issue**: 在GitHub上提交问题
- **社区**: 加入项目讨论群

### 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交代码
4. 发起Pull Request

---

**文档版本**: v1.0  
**最后更新**: 2026-01-19  
**维护人员**: AI Assistant
