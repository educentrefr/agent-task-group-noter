import subprocess
import requests
import mysql.connector
import re
import socket
import fcntl
import struct
import os
import hashlib
import os
from time import sleep

def check_command_output(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def check_debian_version():
    output = check_command_output(['cat', '/etc/os-release'])
    return 'bookworm' in output if output else False

def is_package_installed(pkg_name):
    result = subprocess.run(['dpkg', '-s', pkg_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def check_mysql_version():
    try:
        result = subprocess.run(['mysql', '--version'], stdout=subprocess.PIPE, text=True)
        return 'Ver 8' in result.stdout
    except Exception:
        return False

def check_mysql_password():
    try:
        cnx = mysql.connector.connect(user='root', password='toor')
        cursor = cnx.cursor()
        cursor.execute("SHOW DATABASES;")
        [db[0] for db in cursor.fetchall()]
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return False

def check_php_version(expected_major='8.4'):
    try:
        result = subprocess.run(['php', '-v'], stdout=subprocess.PIPE, text=True)
        return result.stdout.startswith(f'PHP {expected_major}')
    except Exception:
        return False

def check_http_status(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_mysql_database_exists(db_name, user='root', password='toor'):
    try:
        cnx = mysql.connector.connect(user=user, password=password)
        cursor = cnx.cursor()
        cursor.execute("SHOW DATABASES;")
        databases = [db[0] for db in cursor.fetchall()]
        cursor.close()
        cnx.close()
        return db_name in databases
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return False

def get_mac_addresses():
    macs = set()
    try:
        output = check_command_output(['ip', 'link'])
        matches = re.findall(r'link/\w+\s+([0-9a-f:]{17})', output)
        matches = [m.strip() for m in matches if m != '00:00:00:00:00:00']
        macs.update(matches)
    except Exception as e:
        print(f"Error retrieving MAC addresses: {e}")
    return '-'.join(list(macs))


def get_script_hash(filepath=None, algo='sha256'):
    if not filepath:
        filepath = os.path.realpath(__file__)  # get the path to the current script
    hash_func = getattr(hashlib, algo)()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def get_file_content(filepath):
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        return None

def test_xss(serverIpAddress):
    url = f"http://{serverIpAddress}/index.php"
    
    payloads = [
        "<script>pp('hello')</script>",
        "<img src=x onerror=pp('imageError')>",
        "<a href='javascript:coucou(\"linkClick\")'>Click me</a>",
        "<div onmouseover='pp(\"hoverDiv\")'>Hover me</div>",
        "<span onclick='pp(\"clickSpan\")'>Click here</span>",
        "<p><svg onload=pp('svgLoaded')></svg></p>",
        "<button onclick=pp('buttonClick')>Click</button>",
        "<input onfocus=pp('inputFocus') autofocus>",
        "<body onload=pp('bodyLoaded')>",
        "<iframe src='javascript:coucou(\"iframeLoad\")'></iframe>",
        "<marquee onstart=ppp('marqueeStart')>Scroll</marquee>",
        "<form onsubmit=pp('formSubmit')><input type=submit></form>",
    ]

    index = 1
    for payload in payloads:
        print(f"Attack #{index}...")
        data = {"comment": payload, "username": payload, "password": payload}
        requests.post(url, data=data)
        sleep(2)
        index = index + 1

    payloads = [
        "' OR '1'='1",
        "' OR 1=1--",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "' OR ''='",
        "' OR 1=1#",
        "' OR 1=1/*",
        "';--",
        "'; DROP TABLE users; --",
        "' OR 1=1 LIMIT 1 --",
        "' OR EXISTS(SELECT * FROM users) --",
        "' OR (SELECT COUNT(*) FROM users) > 0 --",
        "' AND 1=0 UNION SELECT null, 'hacked' --",
        "' UNION SELECT 1,2,3 --",
        "' UNION SELECT null, version() --",
        "' UNION SELECT username, password FROM users --",
        "' OR SLEEP(5)--",
        "' OR 1=1 AND SLEEP(3)--",
        "' AND (SELECT COUNT(*) FROM information_schema.tables)>0 --",
        "' AND ASCII(SUBSTRING(@@version,1,1))=52 --",
        "'; EXEC xp_cmdshell('whoami')--",
        "' AND 1=CONVERT(int, (SELECT @@version))--",
        "\" OR \"1\"=\"1",
        "\" OR 1=1--",
        "\" OR EXISTS(SELECT * FROM users) --",
        "\" OR (SELECT COUNT(*) FROM users) > 0 --",
        "' OR 'x'='x",
        "' OR 'x'='x'--",
        "' OR 1=1 ORDER BY 1--",
        "' OR 1=1 ORDER BY 2--",
        "' OR 1=1 ORDER BY 3--",
        "' OR 1=1 ORDER BY 4--",
        "PHPSESSID",
    ]

    for payload in payloads:
        print(f"Attack #{index}...")
        data = {"comment": payload, "username": payload, "password": payload}
        requests.post(url, data=data)
        sleep(2)
        index = index + 1

def verify(context):
    analysis = {}
    isServer = input('Is server machine? (y/n): ')
    if isServer.lower() == 'y':
        print("Server machine mode.")
        analysis = {
            "debian_version_is_bookworm": check_debian_version(),
            "ssh_server_installed": is_package_installed('openssh-server'),
            "sudo_installed": is_package_installed('sudo'),
            "apache2_installed": is_package_installed('apache2'),
            "mysql_version_is_8": check_mysql_version(),
            "mysql_password_is_toor": check_mysql_password(),
            "php_version_is_8.2": check_php_version('8.2'),
            "phpmyadmin_served": check_http_status('http://localhost/login.php'),
            "database_exists": check_mysql_database_exists('security_vul'),
            "mac_addresses": get_mac_addresses(),
            "script_hash_sha256": get_script_hash(),
            'suricata.rules': get_file_content('/etc/suricata/rules/suricata.rules'),
            'fast.log': get_file_content('/var/log/suricata/fast.log')
        }
        print("Please run the command on the attacking machine ...")
        isFinished = input('Has the attack finished? (y/n): ')
        if isFinished.lower() == 'y':
            return {
                'isServer': True,
                'analysis' : analysis
            }
    else:
        print("Attack machine mode.")
        serverIpAddress = input('Server IP address to attack: ')
        test_xss(serverIpAddress)
        analysis = {
            'serverIpAddress': serverIpAddress
        }
    return {
        'isServer': isServer,
        'analysis' : analysis
    }
