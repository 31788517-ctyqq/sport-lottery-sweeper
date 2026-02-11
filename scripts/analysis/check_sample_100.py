with open('data/seed/sport_lottery_sample_data.sql', 'r', encoding='utf-8') as f:
    content = f.read()

if '100' in content.lower():
    print('Found 100 in sample data')
    lines = [line for line in content.split('\n') if '100' in line.lower()]
    print(f'Lines with 100: {len(lines)}')
    for line in lines[:5]:
        print(line.strip())
else:
    print('No 100 found in sample data')