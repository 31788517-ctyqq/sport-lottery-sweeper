import chardet

with open('backend/main.py', 'rb') as f:
    result = chardet.detect(f.read())
    print(f'Detected encoding: {result}')