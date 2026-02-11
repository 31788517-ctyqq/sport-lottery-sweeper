"""Rename date_time_int column to date_time in football_matches

Revision ID: rename_date_time_int_to_date_time
Revises: f140b46db4f2
Create Date: 2026-02-12 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'rename_date_time_int_to_date_time'
down_revision: Union[str, None] = 'f140b46db4f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands to rename date_time_int to date_time ###
    # SQLite不支持直接重命名列，需要先添加新列，复制数据，然后删除旧列
    
    # 1. 添加新列 date_time（允许为空，因为要立即填充数据）
    op.add_column('football_matches', 
                  sa.Column('date_time', sa.Integer(), nullable=True, 
                           comment='期号，如 26024'))
    
    # 2. 从source_attributes中提取期号数据来填充date_time
    # 首先添加一个临时函数来处理JSON数据
    op.execute("""
    UPDATE football_matches 
    SET date_time = CAST(json_extract(source_attributes, '$.date_time_int') AS INTEGER)
    WHERE json_extract(source_attributes, '$.date_time_int') IS NOT NULL
    """)
    
    # 3. 对于没有source_attributes数据的记录，尝试从match_id中解析期号
    op.execute("""
    UPDATE football_matches 
    SET date_time = CAST(SUBSTR(match_id, 1, INSTR(match_id, '_') - 1) AS INTEGER)
    WHERE date_time IS NULL AND match_id LIKE '%_%'
    """)
    
    # 4. 设置默认值给剩余的空值（设为0，后续可以通过process_100qiu_data.py重新获取）
    op.execute("UPDATE football_matches SET date_time = 0 WHERE date_time IS NULL")
    
    # 5. 删除旧列 date_time_int（注意：SQLite中列会保持nullable=true，但我们在模型中定义为nullable=false）
    op.drop_column('football_matches', 'date_time_int')


def downgrade() -> None:
    # ### commands to restore date_time_int from date_time ###
    # 1. 添加回旧列 date_time_int
    op.add_column('football_matches', 
                  sa.Column('date_time_int', sa.Integer(), nullable=False, 
                           server_default='0', comment='期号，如 26024'))
    
    # 2. 从date_time复制数据回date_time_int
    op.execute('UPDATE football_matches SET date_time_int = date_time')
    
    # 3. 删除新列 date_time
    op.drop_column('football_matches', 'date_time')
