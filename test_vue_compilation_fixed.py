import requests
import sys

# 测试Vue文件编译
vue_url = "http://localhost:3000/src/views/admin/MobileBeidanFilter.vue"

try:
    print(f"Requesting Vue file: {vue_url}")
    response = requests.get(vue_url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Length: {len(response.text)}")
    
    # 检查内容 - 使用二进制写入避免编码问题
    with open("vue_file_response.bin", "wb") as f:
        f.write(response.content)
    print("Saved response to vue_file_response.bin")
    
    # 尝试解码为UTF-8
    try:
        decoded = response.content.decode('utf-8')
        print(f"\nFirst 300 characters (UTF-8):")
        print(decoded[:300])
        
        # 检查关键内容
        if "Mobile Beidan Filter - SIMPLIFIED TEST" in decoded:
            print("\nOK: Found our simplified test component")
        if "export default" in decoded or "__vite_ssr_import" in decoded:
            print("OK: Contains Vue/JS exports")
            
        # 检查是否有错误
        if "SyntaxError" in decoded or "ReferenceError" in decoded:
            print("\nERROR: Found JavaScript error")
            
    except UnicodeDecodeError:
        print("\nWARNING: Could not decode as UTF-8")
        
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)