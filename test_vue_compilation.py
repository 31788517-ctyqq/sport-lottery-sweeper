import requests

# 测试Vue文件编译
vue_url = "http://localhost:3000/src/views/admin/MobileBeidanFilter.vue"

try:
    print(f"Requesting Vue file: {vue_url}")
    response = requests.get(vue_url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Length: {len(response.text)}")
    
    # 检查内容
    content = response.text
    print(f"\nFirst 500 characters:")
    print(content[:500])
    
    # 检查是否有编译错误信息
    if "Error" in content or "error" in content:
        print("\nWARNING: Found error in response")
    
    # 检查是否是JavaScript（Vue文件应该被编译成JS）
    if "export default" in content or "import" in content:
        print("\nOK: Looks like compiled JavaScript")
    else:
        print("\nWARNING: Doesn't look like compiled JavaScript")
        
    # 保存响应
    with open("vue_file_response.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved response to vue_file_response.txt")
    
except Exception as e:
    print(f"Error: {e}")