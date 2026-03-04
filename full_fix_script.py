#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整修复BeidanFilterPanel.vue中所有可能导致卡片显示问题的脚本
"""

import re
import os

def full_fix_beidan_panel():
    """执行完整的修复过程"""
    file_path = 'c:/Users/11581/Downloads/sport-lottery-sweeper/frontend/src/views/admin/BeidanFilterPanel.vue'
    
    print("开始执行完整修复...")
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    
    # 标记是否已经处理了setup返回部分
    in_setup_return = False
    processed_return = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 检查是否进入setup返回部分
        if 'return {' in line and not processed_return:
            in_setup_return = True
            processed_return = True
            fixed_lines.append(line)
            
            # 跳过直到找到结束的 }
            i += 1
            while i < len(lines):
                current_line = lines[i]
                
                # 如果遇到返回对象的结束，则添加修复后的返回对象
                if '}' in current_line and is_closing_brace(current_line, lines[:i]):
                    break
                
                i += 1
            
            # 添加修复后的返回对象
            fixed_return_object = [
                "      filterForm,",
                "      strengthOptions,",
                "      winPanOptions,",
                "      stabilityOptions,",
                "      rawMatches,",
                "      filterResults,",
                "      loading,",
                "      totalResults,",
                "      currentPage,",
                "      pageSize,",
                "      statistics,",
                "      showStats,",
                "      showAnalysisDialog,",
                "      analysisData,",
                "      availableLeagues,",
                "      dateTimeOptions,",
                "      strategyOptions,",
                "      selectedStrategyName,",
                "      selectedStrategy,",
                "      strategyApplied,",
                "      strategyPreviewMap,",
                "      pagedResults,",
                "      showRulesDialog,",
                "      pLevelRules,",
                "      strategyDetailItems,",
                "      formatMatchTime,",
                "      fetchRealData,",
                "      loadStrategyOptions,",
                "      handleSelectStrategy,",
                "      fetchDateTimeOptions,",
                "      applyAdvancedFilter,",
                "      resetFilters,",
                "      toggleStats,",
                "      exportResults,",
                "      viewDetails,",
                "      getPLevelTagType,",
                "      handleSortChange,",
                "      handleSizeChange,",
                "      handleCurrentChange,",
                "      handleSaveStrategy,",
                "      directionWarning,",
                "      applyPreset,",
                "      fetchPLevelRules",
                "    "
            ]
            
            for fixed_line in fixed_return_object:
                fixed_lines.append(fixed_line)
            fixed_lines.append(current_line)
            continue
        
        # 检查是否有重复声明
        if 'const pagedResults = ref([]);' in line:
            print(f"跳过重复声明: {line}")
            i += 1
            continue
            
        # 检查是否有重复的返回项
        if 'pagedResults,' in line and any(x in lines[i-1] for x in ['showRulesDialog,', 'strategyApplied,']):
            print(f"跳过重复返回项: {line}")
            i += 1
            continue
            
        if 'strategyApplied,' in line and i+1 < len(lines) and 'strategyApplied,' in lines[i+1]:
            print(f"跳过重复返回项: {line}")
            i += 2  # 跳过两行
            continue
            
        if 'strategyPreviewMap,' in line and i+1 < len(lines) and 'strategyPreviewMap,' in lines[i+1]:
            print(f"跳过重复返回项: {line}")
            i += 2  # 跳过两行
            continue
            
        if 'showRulesDialog,' in line and i+1 < len(lines) and 'showRulesDialog,' in lines[i+1]:
            print(f"跳过重复返回项: {line}")
            i += 2  # 跳过两行
            continue
            
        # 检查是否是注释混入返回对象的问题
        if '// 控制统计信息显示' in line or '// 此处不再重复声明已在上方定义的响应式变量' in line:
            if in_setup_return and not '}' in line:
                print(f"跳过返回对象中的注释: {line}")
                i += 1
                continue
        
        # 检查是否是computed定义被注释的问题
        if '// pagedResults已在前面声明为ref，此处使用相同的响应式变量' in line:
            print(f"跳过被注释的定义: {line}")
            i += 1
            continue
        elif 'const pagedResults = computed' in line and '//' in line:
            print(f"跳过被注释的computed定义: {line}")
            i += 1
            continue
        elif 'const pagedResults = computed' in line:
            # 如果还没有添加computed定义，则添加
            if not has_computed_paged_results(content):
                print("添加pagedResults的computed定义")
                # 查找setup函数内的合适位置插入
                fixed_lines.extend([
                    "    // 修复：pagedResults应为computed属性，用于实现分页功能",
                    "    const pagedResults = computed(() => {",
                    "      const start = (currentPage.value - 1) * pageSize.value;",
                    "      return filterResults.value.slice(start, start + pageSize.value);",
                    "    });",
                    ""
                ])
            i += 1
            continue
        else:
            fixed_lines.append(line)
            i += 1
    
    # 写回文件
    fixed_content = '\n'.join(fixed_lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"完成修复: {file_path}")
    print("修复内容:")
    print("- 移除了重复的变量声明")
    print("- 移除了返回对象中的注释")
    print("- 移除了重复的返回项")
    print("- 确保了pagedResults的computed定义")


def is_closing_brace(line, prev_lines):
    """检查是否是返回对象的结束大括号"""
    # 检查大括号平衡
    brace_count = 0
    for l in prev_lines:
        for char in l:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
    
    # 如果当前行有}且之前的大括号已平衡，则这是结束大括号
    for char in line:
        if char == '}':
            if brace_count == 0:
                return True
            brace_count -= 1
    
    return False


def has_computed_paged_results(content):
    """检查是否已经有pagedResults的computed定义"""
    return 'const pagedResults = computed' in content


if __name__ == '__main__':
    full_fix_beidan_panel()