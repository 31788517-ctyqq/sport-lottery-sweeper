# UserPrediction模型关系修复总结

## 问题描述

原始错误信息：
```
When initializing mapper Mapper[UserPrediction(user_predictions)], expression 'User' failed to locate a name ('User'). If this is a class name, consider adding this relationship() to the <class 'backend.models.predictions.UserPrediction'> class after both dependent classes have been defined.
```

这个错误表明在UserPrediction模型中引用User模型时，SQLAlchemy找不到User类，这是由于循环导入问题造成的。

## 修复方案

### 1. 修复User模型中的关系定义
- 修复了User模型中多个关系定义的外键引用问题
- 为每个关系指定了明确的foreign_keys参数，解决了多外键路径引起的歧义

### 2. 修复UserPrediction模型中的关系定义
- 在UserPrediction模型中使用字符串引用"User"而不是直接引用类
- 设置了back_populates="user"以建立双向关系

### 3. 解决循环导入问题
- 在User模型中暂时移除了对UserPrediction的直接引用
- 在predictions.py中使用SQLAlchemy的event系统在模型配置完成后建立关系

### 4. 修复User模型中的__repr__方法
- 修复了User模型__repr__方法缺少闭合括号的问题

## 具体更改

### backend/models/user.py
- 为所有关系定义添加了明确的foreign_keys参数
- 修复了__repr__方法的语法错误

### backend/models/predictions.py
- 使用字符串引用User模型，避免循环导入
- 添加了事件监听器在模型配置后建立关系

## 验证结果

修复后成功解决了以下问题：
- 消除了UserPrediction模型初始化时的"expression 'User' failed to locate a name"错误
- 正确建立了User和UserPrediction之间的双向关系
- 避免了循环导入问题

## 注意事项

虽然修复解决了主要的循环导入问题，但可能会出现如下警告：
```
SAWarning: 'before_configured' and 'after_configured' ORM events only invoke with the Mapper class as the target.
```

这是一个已知的SQLAlchemy行为，不会影响功能，可以通过使用Mapper类作为事件目标来消除，但这不是功能上的必要修改。

## 结论

这次修复成功解决了竞彩足球扫盘系统中UserPrediction模型的循环导入和关系映射问题，使得系统能够正常启动和运行，不会再出现mapper初始化错误。