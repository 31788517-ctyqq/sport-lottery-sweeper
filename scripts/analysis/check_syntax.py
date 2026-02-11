import ast
import sys

def check_syntax(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            source_code = file.read()
        
        # 尝试解析代码
        ast.parse(source_code)
        print(f"✅ {file_path} 语法检查通过")
        return True
    except SyntaxError as e:
        print(f"❌ {file_path} 语法错误:")
        print(f"   行 {e.lineno}: {e.msg}")
        print(f"   {e.text.strip() if e.text else ''}")
        if e.offset:
            print(f"   {' ' * (e.offset - 1)}^")
        return False
    except Exception as e:
        print(f"❌ 检查 {file_path} 时出现错误: {e}")
        return False

if __name__ == "__main__":
    file_path = r"c:\Users\11581\Downloads\sport-lottery-sweeper\backend\services\task_scheduler_service.py"
    check_syntax(file_path)