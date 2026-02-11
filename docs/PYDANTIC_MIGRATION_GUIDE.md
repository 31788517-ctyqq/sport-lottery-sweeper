# Pydantic V1 到 V2 迁移指南

## 概述
项目中发现多个文件仍在使用已弃用的Pydantic V1风格`@validator`装饰器，需要迁移到Pydantic V2风格的`@field_validator`。

## 主要变更点

### 1. 导入变更
```python
# V1 方式 (已弃用)
from pydantic import BaseModel, validator

# V2 方式 (推荐)
from pydantic import BaseModel, field_validator
```

### 2. 装饰器变更
```python
# V1 方式
@validator('field_name')
def validate_field(cls, v):
    return v

# V2 方式
@field_validator('field_name', mode='before')
@classmethod
def validate_field(cls, v):
    return v
```

### 3. 配置类变更
```python
# V1 方式
class Config:
    validate_assignment = True
    
# V2 方式  
model_config = ConfigDict(
    validate_assignment=True
)
```

## 需要迁移的文件

- `backend/schemas/sp_management.py` - 12个@validator装饰器
- `backend/schemas/user.py` - 7个@validator装饰器  
- `backend/schemas/admin_user.py` - 4个@validator装饰器
- `backend/config_fixed.py` - 1个@validator装饰器
- `backend/config.py` - 1个@validator装饰器

## 迁移优先级
1. **高优先级**: 配置文件 (config.py, config_fixed.py)
2. **中优先级**: 核心业务schemas (user.py, admin_user.py)
3. **低优先级**: 业务schemas (sp_management.py)

## 注意事项
- 迁移前备份原文件
- 逐个文件迁移并测试
- 某些复杂验证逻辑可能需要调整

## 临时解决方案
如果暂时不想迁移，可以在代码顶部添加：
```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
```

但这只是临时措施，建议尽快完成正式迁移。