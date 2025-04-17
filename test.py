import subprocess, getpass, json, re

codeTaskGroup = input('codeTaskGroup: ')
with open(f'{codeTaskGroup}.py', 'r') as f:
    code = f.read()
exec(code)
current_time = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode('utf-8').strip()
results = verify({
    'current_time': current_time,
})
print("Results:", results)