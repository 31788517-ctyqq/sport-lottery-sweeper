import requests
import json

def verify_field_mapping():
    print("=" * 70)
    print("验证前端字段与后端数据的映射关系")
    print("=" * 70)
    
    # 从后端获取真实数据
    response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=0&limit=1')
    backend_data = response.json()
    
    if not backend_data:
        print("无法从后端获取数据")
        return
    
    log = backend_data[0]
    print("后端API返回的实际数据：")
    print(f"  timestamp: {log.get('timestamp')}")
    print(f"  level: {log.get('level')}")
    print(f"  request_path: {log.get('request_path')}")
    print(f"  response_status: {log.get('response_status')}")
    print(f"  duration_ms: {log.get('duration_ms')}")
    print(f"  ip_address: {log.get('ip_address')}")
    print(f"  message: {log.get('message')}")
    print()
    
    print("用户观察到的前端显示（字段标题与值错位）：")
    print("  时间: 2026-01-31T09:48:14  <- 应该是timestamp的值")
    print("  级别: /crawler/task/65    <- 应该是request_path的值")
    print("  请求路径: 500             <- 应该是response_status的值")
    print("  状态码: 272000            <- 应该是duration_ms的值")
    print("  耗时(ms):                 <- 应该是ip_address的值(null)")
    print("  IP地址: Crawler task 65: failed  <- 应该是message的值")
    print("  消息:                     <- 没有显示")
    print()
    
    print("分析错位模式：")
    print("  '时间' 标题显示了正确的 timestamp 值")
    print("  '级别' 标题显示了 request_path 的值")
    print("  '请求路径' 标题显示了 response_status 的值")
    print("  '状态码' 标题显示了 duration_ms 的值")
    print("  '耗时(ms)' 标题显示了 ip_address 的值")
    print("  'IP地址' 标题显示了 message 的值")
    print("  '消息' 标题显示为空")
    print()
    
    print("推断可能的原因：")
    print("  1. Element UI el-table 组件在处理数据时出现索引偏移")
    print("  2. 前端数据处理过程中，数组元素顺序发生改变")
    print("  3. 后端返回的数据结构与前端期望不一致")
    print("  4. Vue响应式系统更新DOM时出现错误")
    print()
    
    print("检查前端代码可能的问题：")
    print("  在APILogs.vue中，el-table-column使用了prop属性绑定数据")
    print("  正确的绑定应该是：")
    print("    prop='timestamp' -> label='时间'")
    print("    prop='level' -> label='级别'")
    print("    prop='request_path' -> label='请求路径'")
    print("    prop='response_status' -> label='状态码'")
    print("    prop='duration_ms' -> label='耗时(ms)'")
    print("    prop='ip_address' -> label='IP地址'")
    print("    prop='message' -> label='消息'")
    print()
    
    print("建议解决方案：")
    print("  1. 检查Element UI版本是否是最新的稳定版")
    print("  2. 确认Vue版本兼容性")
    print("  3. 在前端组件中添加key属性以确保列表项正确渲染")
    print("  4. 检查是否有JavaScript错误影响了DOM渲染")
    print("  5. 尝试在el-table上添加: key='tableKey'并每次更新数据时改变key值")

if __name__ == "__main__":
    verify_field_mapping()