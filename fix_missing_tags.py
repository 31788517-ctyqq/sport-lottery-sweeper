#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复BeidanFilterPanel.vue中缺失的结束标签
"""

def fix_missing_tags():
    file_path = r'c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\views\admin\BeidanFilterPanel.vue'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否缺少return的结束大括号和setup函数的结束大括号
    if not content.strip().endswith('}'):
        # 找到最后一个逗号的位置
        last_comma_idx = content.rfind(',')
        if last_comma_idx != -1:
            # 添加缺失的结束大括号
            end_part = content[last_comma_idx+1:].strip()
            if not end_part.endswith('}'):
                # 补充setup函数的结束大括号
                content = content[:last_comma_idx+1] + '\n    },\n};'
    
    # 确保文件以适当的标签结尾
    if not content.strip().endswith('</script>\n</template>'):
        # 查找<script>标签的位置并确保它后面有适当的结束
        script_tag_pos = content.find('<script>')
        if script_tag_pos != -1:
            # 确保有适当的结束
            content = content.rstrip() + '\n</script>\n</template>'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("已修复缺失的结束标签")


if __name__ == '__main__':
    fix_missing_tags()