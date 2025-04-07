sudo apt install python3-pip
sudo mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED.old
sudo apt install -y pkg-config
pip install requests mysql-connector-python

curl -fsSL https://exemple.com/script.sh | bash