import requests
import getpass
import json, subprocess, re

headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/122.0.0.0 Safari/537.36'
    )
}

email = input('Votre email: ')
password = getpass.getpass('Votre mot de passe: ')
codeTaskGroup = input('Code TP: ')

response = requests.post('https://auth.educentre.fr/api/login', json={
    'username': email,
    'password': password
}, headers=headers)
result = response.json()
if 'token' not in result:
    print("Login failed. Please check your credentials.")
    exit(1)
headers['Authorization'] = 'Bearer ' + result['token']

try:
    response = requests.post('https://auth.educentre.fr/api/node/scripts/task-groups/' + codeTaskGroup, json={
    'codeTaskGroup': codeTaskGroup
}, headers=headers)
    response.raise_for_status()
    code = response.text
    exec(code)
    current_time = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode('utf-8').strip()
    results = verify({
        'current_time': current_time,
    })
    current_time = re.sub(r'[^a-zA-Z0-9]', '-', current_time)
    with open(f'node_{current_time}.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("Results:", results)
    results['email'] = email
    results['codeTaskGroup'] = codeTaskGroup
    response = requests.post('https://auth.educentre.fr/api/node/send-data', json=results, headers=headers)
    print(response)
except Exception as e:
    print(f"Failed to download or execute script: {e}")
