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

codeStudentGroup = input('Code groupe: ')

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

def check_mysql_version(expected_version='8.4.3'):
    try:
        result = subprocess.run(['mysql', '--version'], stdout=subprocess.PIPE, text=True)
        return expected_version in result.stdout
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

# Run checks dsdsdsdds
results = {
    "debian_version_is_bookworm": check_debian_version(),
    "ssh_server_installed": is_package_installed('openssh-server'),
    "sudo_installed": is_package_installed('sudo'),
    "apache2_installed": is_package_installed('apache2'),
    "mysql_version_is_8.4.3": check_mysql_version('8.4.3'),
    "mysql_password_is_toor": check_mysql_password(),
    "php_version_is_8.4": check_php_version('8.4'),
    "phpmyadmin_configured": os.path.exists('/var/www/html/phpmyadmin/RELEASE-DATE-5.2.2'),
    "phpmyadmin_served": check_http_status('http://localhost/phpmyadmin'),
    "zabbix_database_exists": check_mysql_database_exists('zabbix'),
    "zabbix_served": check_http_status('http://localhost/zabbix'),
    "mac_addresses": get_mac_addresses(),
    "script_hash_sha256": get_script_hash(),
}
print(results)
