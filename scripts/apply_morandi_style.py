#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端UI优化脚本
用于实现莫兰迪色风格的前端UI设计
"""

import os
import re
from pathlib import Path


def apply_morandi_colors_to_vue_components():
    """向Vue组件应用莫兰迪色系"""
    
    # 莫兰迪色系定义
    MORANDI_COLORS = {
        "rose_quartz": "#C19A92",  # 玫瑰石英粉
        "sage_green": "#9CAD83",   # 鼠尾草绿
        "dusty_blue": "#7BA0C0",   # 土耳其蓝
        "dusty_rose": "#D6B7A8",   # 柔和玫瑰色
        "limestone": "#BFC0AB",     # 石灰岩灰
        "muted_peach": "#F0DBCE",   # 柔和桃色
        "dusky_lavender": "#A8A1C0", # 暗薰衣草紫
        "light_sage": "#D2DCC5",    # 浅鼠尾草色
        "warm_taupe": "#BDA79B",    # 温暖灰褐色
        "soft_grey": "#B8B6B0",     # 柔和灰色
        "blush_pink": "#E2C9C7",    # 淡粉色
        "muted_coral": "#EFA8A3",   # 柔和珊瑚色
    }
    
    # Vue组件文件路径
    vue_files = []
    frontend_src = Path("frontend/src")
    
    if frontend_src.exists():
        # 查找所有Vue文件
        for ext in ["*.vue", "*.js", "*.ts", "*.jsx", "*.tsx", "*.css", "*.scss"]:
            vue_files.extend(list(frontend_src.rglob(ext)))
        
        print(f"找到 {len(vue_files)} 个前端文件")
        
        # 定义颜色替换规则
        color_replacements = {
            # 替换蓝色系
            r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})(?![^<]*>|[^<]*(?=<\/style))': lambda m: replace_with_morandi(m.group(1), MORANDI_COLORS),
            # 替换RGB颜色
            r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)': lambda m: rgb_to_morandi(int(m.group(1)), int(m.group(2)), int(m.group(3)), MORANDI_COLORS),
        }
        
        processed_files = 0
        for file_path in vue_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # 应用颜色替换
                for pattern, replacement_func in color_replacements.items():
                    if isinstance(replacement_func, str):
                        content = re.sub(pattern, replacement_func, content)
                    else:
                        # 复杂替换函数
                        matches = re.findall(pattern, content)
                        for match in matches:
                            if isinstance(match, tuple):
                                # 处理RGB颜色
                                new_color = replacement_func(*match)
                                content = re.sub(pattern, new_color, content, count=1)
                            else:
                                # 处理十六进制颜色
                                new_color = replacement_func(match)
                                content = content.replace(match, new_color)
                
                # 如果内容发生了变化，写回文件
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    processed_files += 1
                    print(f"   已更新: {file_path.name}")
            
            except Exception as e:
                print(f"   处理文件时出错 {file_path.name}: {str(e)}")
        
        print(f"处理了 {processed_files} 个文件")
    else:
        print("未找到前端源码目录 (frontend/src)")


def replace_with_morandi(hex_color, morandi_colors):
    """将普通颜色替换为莫兰迪色"""
    # 简化版本：随机选择一个莫兰迪色替代
    import random
    return random.choice(list(morandi_colors.values()))


def rgb_to_morandi(r, g, b, morandi_colors):
    """将RGB颜色替换为莫兰迪色"""
    import random
    return f"rgb({random.randint(150, 220)}, {random.randint(150, 200)}, {random.randint(150, 220)})"


def create_morandi_style_guide():
    """创建莫兰迪色风格指南文件"""
    
    style_guide_content = """
/* 莫兰迪色系风格指南 */
/* 用于体育彩票扫盘系统的前端UI设计 */

:root {
  /* 主色调 - 玫瑰石英粉 */
  --morandi-rose-quartz: #C19A92;
  --morandi-rose-quartz-light: #D1B8B2;
  --morandi-rose-quartz-dark: #A17A72;

  /* 辅助色 - 鼠尾草绿 */
  --morandi-sage-green: #9CAD83;
  --morandi-sage-green-light: #BDCFB5;
  --morandi-sage-green-dark: #7D8B63;

  /* 辅助色 - 土耳其蓝 */
  --morandi-dusty-blue: #7BA0C0;
  --morandi-dusty-blue-light: #9BC0D0;
  --morandi-dusty-blue-dark: #5B80A0;

  /* 中性色 - 石灰岩灰 */
  --morandi-limestone: #BFC0AB;
  --morandi-limestone-light: #DFE0CB;
  --morandi-limestone-dark: #9F9F8B;

  /* 柔和桃色 */
  --morandi-peach: #F0DBCE;

  /* 柔和灰色 */
  --morandi-grey: #B8B6B0;
}

/* 应用到表格组件 */
.el-table {
  --el-table-border-color: var(--morandi-limestone-light);
  --el-table-text-color: #333;
}

/* 应用到卡片组件 */
.el-card {
  background-color: var(--morandi-peach);
  border: 1px solid var(--morandi-limestone);
  border-radius: 8px;
}

/* 应用到按钮组件 */
.el-button--primary {
  background-color: var(--morandi-sage-green);
  border-color: var(--morandi-sage-green);
}

.el-button--primary:hover {
  background-color: var(--morandi-sage-green-light);
  border-color: var(--morandi-sage-green-light);
}

/* 应用到输入框 */
.el-input__wrapper {
  background-color: #f9f9f9;
  border: 1px solid var(--morandi-limestone);
}

/* 应用到标签 */
.el-tag {
  background-color: var(--morandi-rose-quartz-light);
  border-color: var(--morandi-rose-quartz);
  color: #555;
}

/* 应用到状态指示器 */
.status-online {
  background-color: var(--morandi-sage-green) !important;
}

.status-offline {
  background-color: var(--morandi-grey) !important;
}

.status-running {
  background-color: var(--morandi-dusty-blue) !important;
}

/* 应用到表单卡片 */
.form-card {
  background-color: var(--morandi-peach);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(193, 154, 146, 0.1);
}

/* 应用到数据表格 */
.data-table {
  background-color: white;
  border-collapse: collapse;
  width: 100%;
}

.data-table th {
  background-color: var(--morandi-limestone-light);
  color: #333;
  font-weight: 500;
}

.data-table td, .data-table th {
  border: 1px solid var(--morandi-limestone);
  padding: 10px;
}

/* 应用到导航栏 */
.navbar {
  background-color: var(--morandi-rose-quartz);
  padding: 16px;
  border-bottom: 1px solid var(--morandi-limestone);
}
"""
    
    # 写入风格指南文件
    with open("frontend/src/styles/morandi-theme.scss", "w", encoding="utf-8") as f:
        f.write(style_guide_content)
    
    print("✅ 莫兰迪色风格指南已创建: frontend/src/styles/morandi-theme.scss")


def update_element_plus_theme():
    """更新Element Plus主题以使用莫兰迪色"""
    
    theme_content = """
// 莫兰迪色主题定制
@forward 'element-plus/theme-chalk/src/common/var.scss' with (
  $colors: (
    'primary': (
      'base': #9CAD83,  // 鼠尾草绿
    ),
    'success': (
      'base': #C19A92,  // 玫瑰石英粉
    ),
    'warning': (
      'base': #D6B7A8,  // 柔和玫瑰色
    ),
    'danger': (
      'base': #A8A1C0,  // 暗薰衣草紫
    ),
    'info': (
      'base': #7BA0C0,  // 土耳其蓝
    ),
  )
);

// 引入 Element Plus 的全部样式
@use "element-plus/theme-chalk/src/index.scss" as *;

// 引入自定义莫兰迪色样式
@use "./morandi-theme.scss";
"""
    
    # 写入主题定制文件
    with open("frontend/src/styles/element-morandi.scss", "w", encoding="utf-8") as f:
        f.write(theme_content)
    
    print("✅ Element Plus莫兰迪主题已创建: frontend/src/styles/element-morandi.scss")


def update_package_json():
    """更新package.json以包含normalize.css依赖"""
    
    import json
    
    package_path = "frontend/package.json"
    
    if os.path.exists(package_path):
        with open(package_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        # 添加normalize.css到依赖
        if 'dependencies' not in package_data:
            package_data['dependencies'] = {}
        
        package_data['dependencies']['normalize.css'] = "^8.0.1"
        
        # 保存更新后的package.json
        with open(package_path, 'w', encoding='utf-8') as f:
            json.dump(package_data, f, indent=2, ensure_ascii=False)
        
        print("✅ normalize.css已添加到前端依赖")
    else:
        print("⚠️ 未找到package.json文件")


def run_morandi_style_application():
    """运行莫兰迪风格应用"""
    print("=" * 60)
    print("前端UI莫兰迪色风格应用")
    print("=" * 60)
    
    print("\n🔍 正在应用莫兰迪色系到前端组件...")
    apply_morandi_colors_to_vue_components()
    
    print("\n🔍 正在创建莫兰迪色风格指南...")
    create_morandi_style_guide()
    
    print("\n🔍 正在更新Element Plus主题...")
    update_element_plus_theme()
    
    print("\n🔍 正在更新前端依赖...")
    update_package_json()
    
    print("\n🎉 莫兰迪色风格已应用到前端UI!")
    print("\n下一步操作建议:")
    print("- 检查生成的样式文件并根据需要调整")
    print("- 在main.js中引入新的样式文件")
    print("- 测试UI组件以确保颜色搭配合适")
    print("- 调整对比度以确保可读性")


if __name__ == "__main__":
    run_morandi_style_application()