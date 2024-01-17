#!/bin/bash

## File: load.sh
## Author: Russell Loewe
## Date: July 20, 2022
## Contact: russloewe@gmail.com
## Description: Shell commands to setup a new webapp on a clean 
##              ubuntu server install. Load these functions into another 
##              shell script along with the environment file in 
##              /loewetechsoftware_com/loewetechsoftware_com/.env
## Notes:  
##         *This script requires that the remote host has PermitRootLogin,
##         a password for root and a user with sudo privliges. 
##         More info below. 
##         *On virtural box make sure host machine network is in 
##          bridge adapter
## Requires: sftp, ssh, sshpass

# Load environment variables from ./loewetechsoftware_com/.env
source ./loewetechsoftware_com/.env

echo "Moving to local app source directory: ${APPSRC}"
cd ${APPSRC}

# The following are defined in the .env file that must be loaded by the 
# calling shell script
#HOST=  # Host IP
# Credentials
#PASS=
#REMOTE_USER=
#REMOTE_PASS=
#APPDIR=/var/loewetechsoftware_com # Remote Directory for Django source code
#APPSRC=/home/russell/Dropbox/loewetechsoftware_com # Location for local codebase
#VENDIR=/var/venv_logger # Remote Directory for python virtual environment


run() {
	echo 'running'
	check_vars
	
	#InitSSHKeys
	#SetupFirewall
	#InstallDependencies
	#OpenPsql
	SetupDjangoServer
	#InitDB
	#SetupVenv
	#SetupPostgresql
	#SetupApache
	}

# Do these commands on remote server to allow this script to run
# 1) set root password:
# sudo -s
# passwd 
# 2) enable root ssh login:
# add 'PermitRootLogin yes' to /etc/ssh/sshd_config
# sudo systemctl restart sshd
#
# 3) if this script still cant login try ssh from terminal and save host fingerprint then retry this script


check_vars() {
	echo "VENDIR=$VENDIR"
	echo "APPSRC=$APPSRC"
	echo "APPDIR=$APPDIR"
	echo "HOST=$HOST"
	
	# Check if any of the variables are null
	if [[ -z $VENDIR || -z $APPSRC || -z $APPDIR || -z $HOST ]]; then
	  echo "Error: One or more variables are null."
	  exit 1
	else
	  echo "All variables are not null."
	fi
}

add_line () {
	# Define the line to be added

	file="$1"
	line="$2"
	# Check if the file already contains the line
	if remote_command "grep -Fxq '$line' $file;"; then
		echo "$line already exists in the file."
	else
		# Add the line to the file
		remote_command "echo '$line' >> $file"
		echo "$line has been added to the file."
	fi
}

# helper functions 
upload_file () {
    # Upload single file
    # Arg 1: remote dest dir
    # Arg 2: full path to local file
    DIR="$1"
    REMOTE_CMD="put $2"
    sftp root@${HOST}:${DIR} <<< $REMOTE_CMD
}

upload_folder () {
    # Upload single file
    # Arg 1: local path
    # Arg 2: path on remote server
    REMOTE_CMD="put -r $1"
    DIR="$2"
    sftp root@${HOST}:${DIR} <<< $REMOTE_CMD
}


remote_command () {
    ssh root@${HOST} $1
}

remote_new_user () {
	
	echo "creating user $1 at $HOST"
	remote_command "useradd $1; echo $1:$2 | chpasswd"
}
	
# Step 1
InitSSHKeys () {
	# Check that we have ssh keys on local machine and are able to 
	# ssh into root on the remote server
    echo "Checking if local ssh keys exist..."
    if [ -e ~/.ssh/id_rsa.pub ]
    then
        echo "Public key found ~/.ssh/id_rsa.pub"
    else
        echo "No SSH keys found in ~/.ssh/"
        echo "Attempting to generate keys"
        ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ''
        #exit 1
    fi
    
    echo "Checking remote login..."
    sshpass -p "$PASS" ssh root@$HOST 'ls' || { echo 'could not login as root'; echo 'try: sudo -s; passwd, or set "PermitRootLogin yes" in /etc/ssh/sshd_config; also try ssh from terminal and save fingerprint' ; exit 1; }
    
    echo "Uploading pubilic SSH key for root"
    cd ~/.ssh/
    sshpass -p "$PASS" sftp root@$HOST:/root/.ssh/ <<< $'put id_rsa.pub'
    sshpass -p "$PASS" ssh root@$HOST 'rm -rf /root/.ssh/authorized_keys'
    sshpass -p "$PASS" ssh root@$HOST 'mv /root/.ssh/id_rsa.pub  /root/.ssh/authorized_keys'
    
    echo "enabling pubkey authentication"
    sshpass -p "$PASS" ssh root@$HOST 'echo "PubKeyAuthentication yes" >> /etc/ssh/sshd_config'
    
    echo "Restarting remote ssh daemon"
    sshpass -p "$PASS" ssh root@${HOST} 'systemctl restart sshd' 
    
	# At this point we can use remote_command since we dont need sshpass
	# Do this step last so we don't lock ourselves out of the server if there is a problem
	echo "Disabling password login"
    remote_command "sed -i '/PasswordAuthentication yes/d' /etc/ssh/sshd_config"
    
    echo "Restarting remote ssh daemon"
    remote_command 'systemctl restart sshd' 
}

# Step 2 
SetupFirewall () {
    
    echo 'Setting up firewall'
    remote_command 'ufw allow from 10.0.0.0/24 to any port 22 proto tcp' 
    remote_command 'ufw allow 80' 
    remote_command 'ufw allow 443' 
    remote_command 'ufw allow from 10.0.0.0/24 to any port 9494 proto tcp'
    remote_command 'systemctl enable ufw'
    remote_command 'ufw reload'
}

# Step 3
InstallDependencies () {
    
    echo "Updating server"
    remote_command 'apt update'
    remote_command 'apt -y upgrade'
    
    echo 'Installing packages'
    remote_command 'apt -y install apache2'
    remote_command 'apt -y install libapache2-mod-wsgi-py3'
    remote_command 'apt -y install python3.10-venv'
    remote_command 'apt -y install python3-pip'
    remote_command 'apt -y install certbot'
    remote_command 'apt -y install python3-certbot-apache'
    remote_command 'apt -y install sysstat'

}


# Step 5
SetupDjangoServer () {
    
    echo "Setting up app ${APPDIR}"
    
    echo 'Cleaning local *.pyc files'
    find ${APPSRC}  -name '*.pyc'  -delete
    
    echo 'Cleaning remote'
    remote_command "rm -rf ${APPDIR}"

    
    echo 'Uploading server source'
    upload_folder $APPSRC /var/www
    
    echo "Install Apache site config"
    remote_command "rm /etc/apache2/sites-enabled/*"
    remote_command "mv ${APPDIR}/loewetechsoftware_com.conf /etc/apache2/sites-enabled/"
    
    echo "Turning debug off in production server"
    remote_command "mv ${APPDIR}/loewetechsoftware_com/prod.env ${APPDIR}/loewetechsoftware_com/.env"
    
    echo 'setting permissions'
    remote_command "chown www-data:www-data -R ${APPDIR}"
    remote_command "chmod a+x -R ${APPDIR}"
    
    echo "Restarting apache server"
    remote_command "systemctl restart apache2"
    
}


# Step 5.1
SetupVenv () {
    echo "Creating virtual environment: $VENDIR"
    remote_command "python3 -m venv $VENDIR"
    
    upload_file ${APPDIR} $APPSRC/requirements.txt
    
    echo 'Installing python packages'
    #remote_command "source $VENDIR/bin/activate; pip install -r ${APPDIR}/requirements.txt"
    remote_command "source $VENDIR/bin/activate; pip install -r ${APPDIR}/requirements.txt"
    
    echo 'Setting permissions'
    remote_command "chown www-data:www-data -R $VENDIR"
}

SetupLocalVenv () {
    echo "Creating virtual environment: $VENDIR"
    sudo python3 -m venv $VENDIR
    
    echo 'Installing python packages'
    sudo source $VENDIR/bin/activate; pip install -r ${APPSRC}/requirements.txt
    
    echo 'Setting permissions'
    sudo chown www-data:www-data -R $VENDIR
}

# Step 6
InitDB () {
	
	echo "Deleting old database: $DBDIR"
	remote_command "rm -rf $DBDIR"
	remote_command "mkdir $DBDIR"
	
    echo "Uploading database to remote host"
    #upload_file ${DBDIR}/ ${APPSRC}/db/logger.db
    upload_file ${DBDIR}/ ${DBDIR}/logger.db
    
    echo 'Setting permissions on database'
    remote_command "chown www-data:www-data -R $DBDIR"
    remote_command "chmod a+x -R $DBDIR"
}

InitLocalDB () {
	
	echo "Deleting old database: $DBDIR"
	sudo rm -rf $DBDIR
	sudo mkdir $DBDIR
	.
    echo "Copying db to ${DBDIR}"
    sudo cp  ${APPSRC}/db/logger.db ${DBDIR}/
    
    echo 'Setting permissions on database'
    sudo chown www-data:www-data -R $DBDIR
    sudo chmod a+xrw -R $DBDIR
}

# Step 6 B
SetupPostgresql () {
	
	echo "Setting up Postgresql on $HOST"
	remote_command "apt install -y postgresql postgresql-contrib"
	remote_command "systemctl start postgresql.service"
	
	echo "Creating user: $DB_USER, (ignore the 'could not change directory to /root' errors)"
	remote_new_user $DB_USER $DB_PASS
    
    echo "Adding user $DB_USER to sudo group"
	remote_command "usermod -aG sudo $DB_USER"
    
    echo "Creating postgres user $DB_USER"
	remote_command "sudo -u postgres createuser $DB_USER"
    
    echo "Creating database $DB_NAME"
	remote_command "sudo -u postgres createdb ${DB_NAME}"
}

MigrateToPostgresql () {
    
    echo 'migrating database to postgresql db'
    
    echo 'Taking server down'
    remote_command "systemctl stop apache2"
    
    echo 'dumping current db to ./datadump.json'
    remote_command "source $VENDIR/bin/activate; python3 $APPDIR/manage.py dumpdata > datadump.json"
    

    echo "Bringing server back online"
    remote_command "systemctl start apache2"
}


# Step 7 
SetupApache () {
    
    echo 'Enabling WSGI mod'
    remote_command 'a2enmod wsgi'
    remote_command 'a2enmod ssl'
    
    #echo 'backing up apache default config and port.conf'
    #remote_command 'cp /etc/apache2/sites-enabled/000-default.conf ~/'
    #remote_command 'cp /etc/apache2/ports.conf /etc/apache2/ports.conf.bk'
    
    #echo 'Removing default config'
    #remote_command 'rm -rf /etc/apache2/sites-enabled/*'
    
    #echo 'Uploading apache conf file'
    #upload_file /etc/apache2/sites-enabled/ $APPSRC/loewelogger_http_dev.conf
    
    #echo 'Removing apache listing port 80 (needed for certbot automated tool)'
    #remote_command "sed -i '/Listen 80/d' /etc/apache2/ports.conf"
    
    #add_line /etc/apache2/ports.conf 'Listen 8080'
    add_line /etc/apache2/ports.conf 'Listen 9494'
    
    echo "Restarting apache"
    remote_command 'systemctl restart apache2'
    
}

# Step 8
SetupCertBot () {
    
    echo 'Setting up CertBot'
    remote_command  'apt-get -y install certbot python3-certbot-apache'
    
    echo 'Starting certbot'
    remote_command 'certbot certonly --standalone'
}

# Step 9
RestartApache () {
    
    # Assumes apache was enabled and started in SetupApache above ^
    echo 'Restarting apache2 server'
    remote_command 'systemctl restart apache2'
}

GetApacheErrorLogs () {

	echo "################## systemctl status apache2.service: ${HOST}"
    echo '################## systemctl status apache2.service'  > ${APPSRC}/remote_errors.log
    remote_command 'systemctl status apache2.service'      >> ${APPSRC}/remote_errors.log
    
    echo "################## journalctl -xeu apache2.service: ${HOST}"
    echo '################## journalctl -xeu apache2.service'   >> ${APPSRC}/remote_errors.log
    remote_command 'journalctl -xeu apache2.service'       >> ${APPSRC}/remote_errors.log
    
    echo "################## /loewetechsoftware_com/server_errors.log: ${HOST}"
    echo '################## /loewetechsoftware_com/server_errors.log' >> ${APPSRC}/remote_errors.log
    remote_command "cat ${APPDIR}/server_errors.log" >> ${APPSRC}/remote_errors.log
}

OpenPsql () {
	
	echo "Opening psql session on ${HOST}"
	remote_command "sudo -u postgres psql"
}

run
