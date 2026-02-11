import re

with open('backend/models/user_models.py', 'r', encoding='utf-8') as f:
    content = f.read()
    matches = re.findall(r'class\s+(\w+)\s*\(.*?\):', content, re.DOTALL)
    print('Classes found:', matches)