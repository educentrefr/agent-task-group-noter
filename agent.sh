#!/bin/bash

echo "== Installation de l'agent =="
sudo apt update
sudo apt install -y python3-pip
if [ -f /usr/lib/python3.11/EXTERNALLY-MANAGED ]; then
    sudo mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED.old
fi
sudo apt install -y pkg-config
pip install requests mysql-connector-python
wget -qO educentre-agent.py http://localhost:8080/agent.py  
python3 educentre-agent.py
rm educentre-agent.py
