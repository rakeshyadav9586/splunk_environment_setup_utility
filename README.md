# splunk_environment_setup_utility
Utility to make our job easy for Splunk environment setup

# Features

  - Splunk App install/upgrade, Reinstall
  - Splunk install/upgrade, Reinstall
  - Distributed Setup, Remove
  - Cluster Setup: Splunk install/Upgrade, Reinstall
  - Cluster Setup, Resetup
  - Cluster App push on Indexer and Search Head

### Prerequisites:
Server: Ubuntu Server (CLI) Installation

### Execute the below commands to install the packages:
```ssh
apt-get install -y wget
apt-get update
apt-get install build-essential libssl-dev libffi-dev python-dev
apt install python3-pip
apt upgrade python3-pip
python3 -m pip install --upgrade pip
check virtual environment : which virtualenv
apt install -y python3-venv
apt-get install vpnc
apt install sshpass
pip3 install Flask-WTF
pip3 install paramiko
pip3 install request
pip3 install pexpect
pip3 install shelljob
```

### Create a Directory
```ssh
cd /opt
mkdir Flask_Project
cd Flask_Project
python3 -m venv rakesh
```
Clone the repo here
```ssh
. rakesh/bin/activate
once work is done then 'deactivate'
```

### Turn On the server
```ssh
cd /opt/Flask_Project
. rakesh/bin/activate
python3 yadav.py
```

### Note
I have added print statement for debug purpose kindly ignore it as it's not considered in code best practices

### Things need to be taken care
- Update the Server 'host' and 'port' from 'yadav.py' file in below row
```ssh
app.run(host='10.0.0.1', port=8000, threaded=True, debug = True)
```
- Update the Server 'host' and 'port' from templates>result.html in below row
```ssh
For a new request click <a href="http://10.0.0.1:8000/">Home</a>
```
- Update the license file which placed into 'Splunk_Setup' directory from executed_scripts > Script4.py in below row
```ssh
self.license_file = "Rakesh_Yadav.License"
```
- Add the splunk file into 'Splunk_Setup' directory
```ssh
For example: splunk-8.0.4-767223ac207f-Linux-x86_64.tgz
```

### Kill the running process
```sh
lsof -i -P -n | grep LISTEN
kill -9 'Enter_PID'
```

#### Remove already saved key from Ubuntu server
```sh
ssh-keygen -f "/root/.ssh/known_hosts" -R "Enter_IP"
```


License
----
No License