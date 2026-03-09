import subprocess, sys
result = subprocess.run([sys.executable, 'test_all_models.py'], capture_output=True, text=True)
print('STDOUT:')
print(result.stdout)
print('STDERR:')
print(result.stderr)
print('Return code:', result.returncode)