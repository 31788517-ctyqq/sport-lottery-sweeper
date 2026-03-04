#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
精确修复BeidanFilterPanel.vue中导致卡片显示问题的关键部分
"""

def precise_fix():
    file_path = r'c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\views\admin\BeidanFilterPanel.vue'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 确保只有computed定义，没有ref重复定义
    # 先移除可能的pagedResults ref定义
    content = content.replace("const pagedResults = ref([]);", "")
    
    # 2. 确保有正确的computed定义
    if "const pagedResults = computed" not in content:
        # 在setup函数的合适位置添加computed定义
        # 查找filterResults定义后添加
        insert_pos = content.find("const filterResults = ref([]);")
        if insert_pos != -1:
            insert_pos = content.find(";", insert_pos) + 1  # 找到分号后的位置
            paged_results_def = """
    // pagedResults的computed定义，用于实现分页功能
    const pagedResults = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value;
      return filterResults.value.slice(start, start + pageSize.value);
    });
""" 
            content = content[:insert_pos] + paged_results_def + content[insert_pos:]
    
    # 3. 修复setup函数返回部分，移除重复和注释
    # 找到return { 开始的位置
    return_start = content.find("return {")
    if return_start != -1:
        # 找到对应的结束位置
        brace_count = 0
        pos = return_start
        while pos < len(content):
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
            pos += 1
        
        if brace_count == 0:
            # 提取返回对象内容
            return_content = content[return_start:pos+1]
            
            # 构建干净的返回对象
            clean_return_part = """    return {
      filterForm,
      strengthOptions,
      winPanOptions,
      stabilityOptions,
      rawMatches,
      filterResults,
      loading,
      totalResults,
      currentPage,
      pageSize,
      statistics,
      showStats,
      showAnalysisDialog,
      analysisData,
      availableLeagues,
      dateTimeOptions,
      strategyOptions,
      selectedStrategyName,
      selectedStrategy,
      strategyApplied,
      strategyPreviewMap,
      pagedResults,
      showRulesDialog,
      pLevelRules,
      strategyDetailItems,
      formatMatchTime,
      fetchRealData,
      loadStrategyOptions,
      handleSelectStrategy,
      fetchDateTimeOptions,
      applyAdvancedFilter,
      resetFilters,
      toggleStats,
      exportResults,
      viewDetails,
      getPLevelTagType,
      handleSortChange,
      handleSizeChange,
      handleCurrentChange,
      handleSaveStrategy,
      directionWarning,
      applyPreset,
      fetchPLevelRules
    }"""
            
            # 替换原有的返回对象
            content = content[:return_start] + clean_return_part + content[pos+1:]
    
    # 4. 移除可能的重复注释
    content = content.replace("// 控制统计信息显示\n", "")
    content = content.replace("// 此处不再重复声明已在上方定义的响应式变量\n", "")
    content = content.replace("// analysisData, availableLeagues, dateTimeOptions, strategyOptions,\n", "")
    content = content.replace("// selectedStrategyName, selectedStrategy, strategyApplied, strategyPreviewMap\n", "")
    content = content.replace("// 均已在前面声明\n", "")
    content = content.replace("// 计算属性 pagedResults 已在上面定义过，这里重写\n", "")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("精确修复完成！")
    print("- 移除了pagedResults的重复ref声明")
    print("- 确保了pagedResults的computed定义")
    print("- 清理了setup返回对象中的重复项和注释")
    print("- 保留了所有必要的返回项")

if __name__ == '__main__':
    precise_fix()