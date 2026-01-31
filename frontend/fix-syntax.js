#!/usr/bin/env node

const fs = require('fs')
const path = require('path')

const API_MODULES_DIR = path.join(__dirname, 'frontend/src/api/modules')

// 修复函数
function fixApiSyntax(content) {
  let fixed = content
  
  // 1. 替换旧的request导入为新的http导入
  fixed = fixed.replace(
    /import request from '@\/utils\/request'/g,
    "import http from '@/utils/http'"
  )
  
  // 2. 替换request调用为http调用
  fixed = fixed.replace(
    /return request\(\{\s*url:\s*'([^']+)'\s*,\s*method:\s*'([^']+)'\s*(?:,\s*([^}]+))?\s*\}\)/g,
    (match, url, method, otherProps) => {
      // 移除/api前缀
      const newUrl = url.replace(/^\/api/, '')
      
      if (method === 'get') {
        const paramsMatch = otherProps?.match(/params:\s*([^,}]+)/)
        const params = paramsMatch ? `, { params: ${paramsMatch[1]} }` : ''
        return `return http.get('${newUrl}'${params})`
      } else if (method === 'post') {
        const dataMatch = otherProps?.match(/data:\s*([^,}]+)/)
        const data = dataMatch ? `, ${dataMatch[1]}` : ''
        return `return http.post('${newUrl}'${data})`
      } else if (method === 'put') {
        const dataMatch = otherProps?.match(/data:\s*([^,}]+)/)
        const data = dataMatch ? `, ${dataMatch[1]}` : ''
        return `return http.put('${newUrl}'${data})`
      } else if (method === 'delete') {
        const dataMatch = otherProps?.match(/data:\s*([^,}]+)/)
        if (dataMatch) {
          return `return http.delete('${newUrl}', { data: ${dataMatch[1]} })`
        } else {
          return `return http.delete('${newUrl}')`
        }
      } else if (method === 'patch') {
        const dataMatch = otherProps?.match(/data:\s*([^,}]+)/)
        const data = dataMatch ? `, ${dataMatch[1]}` : ''
        return `return http.patch('${newUrl}'${data})`
      }
      
      return match
    }
  )
  
  // 3. 修复FormData上传
  fixed = fixed.replace(
    /const formData = new FormData\(\)[\s\S]*?return request\(\{\s*url:\s*'([^']+)'[\s\S]*?\}\)/g,
    (match, url) => {
      const newUrl = url.replace(/^\/api/, '')
      return match.replace(`return request({`, `return http.upload('${newUrl}', file)`)
    }
  )
  
  // 4. 修复文件下载
  fixed = fixed.replace(
    /responseType:\s*'blob'[\s\S]*?return request\(\{\s*url:\s*'([^']+)'[\s\S]*?\}\)/g,
    (match, url) => {
      const newUrl = url.replace(/^\/api/, '')
      return match.replace(`return request({`, `return http.download('${newUrl}', params, 'download.xlsx')`)
    }
  )
  
  // 5. 确保每个函数都有正确的闭合
  const lines = fixed.split('\n')
  const fixedLines = []
  let braceCount = 0
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    
    // 计算大括号
    const openBraces = (line.match(/\{/g) || []).length
    const closeBraces = (line.match(/\}/g) || []).length
    
    braceCount += openBraces - closeBraces
    
    fixedLines.push(line)
    
    // 如果这一行结束后braceCount不为0，且下一行是新的export或注释，可能需要添加闭合
    if (braceCount > 0 && i < lines.length - 1) {
      const nextLine = lines[i + 1]
      if (nextLine.trim().startsWith('//') || nextLine.trim().startsWith('export') || nextLine.trim() === '') {
        // 添加缺失的闭合括号
        for (let j = 0; j < braceCount; j++) {
          fixedLines.push('})')
        }
        braceCount = 0
      }
    }
  }
  
  fixed = fixedLines.join('\n')
  
  return fixed
}

// 处理所有API模块文件
function processApiFiles() {
  console.log('🔧 开始修复API模块语法错误...\n')
  
  const files = fs.readdirSync(API_MODULES_DIR)
    .filter(file => file.endsWith('.js'))
  
  let processedCount = 0
  let fixedCount = 0
  
  files.forEach(file => {
    const filePath = path.join(API_MODULES_DIR, file)
    console.log(`📝 处理文件: ${file}`)
    
    try {
      const content = fs.readFileSync(filePath, 'utf8')
      const fixedContent = fixApiSyntax(content)
      
      if (content !== fixedContent) {
        fs.writeFileSync(filePath, fixedContent, 'utf8')
        console.log(`  ✅ ${file} - 已修复`)
        fixedCount++
      } else {
        console.log(`  ℹ️  ${file} - 无需修复`)
      }
      
      processedCount++
    } catch (error) {
      console.error(`  ❌ ${file} - 处理失败:`, error.message)
    }
  })
  
  console.log(`\n📊 修复完成: 处理了 ${processedCount} 个文件，修复了 ${fixedCount} 个文件`)
}

// 执行修复
if (require.main === module) {
  processApiFiles()
}

module.exports = { fixApiSyntax, processApiFiles }