import requests
import getpass

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
headers['Authorization'] = 'Bearer ' + result['token']

try:
    response = requests.post('http://localhost:8080/verify.py', json={
    'codeTaskGroup': codeTaskGroup
}, headers=headers)
    response.raise_for_status()
    code = response.text
    exec(code)
except Exception as e:
    print(f"Failed to download or execute script: {e}")
