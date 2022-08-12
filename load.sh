#!/bin/bash

## File: load.sh
## Author: Russell Loewe
## Date: July 20, 2022
## Contact: russloewe@gmail.com
## Description: Shell commands to setup a new webapp on a clean 
##              ubuntu server install.
## Notes: *This script requires that the remote host has PermitRootLogin,
##         a password for root and a user with sudo privliges. 
##         More info below. 
##         *On virtural box make sure host machine network is in 
##          bridge adapter
## Requires: sftp, ssh, sshpass

source ./loewetechsoftware_com/.env
# The following are defined in the .env file
#HOST=  # Host IP
# Credentials
#PASS=
#REMOTE_USER=
#REMOTE_PASS=
#APPDIR=/var/loewetechsoftware_com # Remote Directory for Django source code
#APPSRC=/home/russell/Dropbox/loewetechsoftware_com # Location for local codebase
#SSLDIR=/etc/apache2/ssl # Remote Directory for installing SSL keys
#VENDIR=/var/venv_logger # Remote Directory for python virtual environment
#DBDIR=/var/db_logger # DB directory for sqlite3 database


# Do these commands on remote server to allow this script to run
# sudo -s
# passwd 
# add 'PermitRootLogin yes' to /etc/ssh/sshd_config
# sudo systemctl restart sshd

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
    # Arg 1: remote dest dir
    # Arg 2: full path to local folder
    DIR="$1"
    REMOTE_CMD="put  -r $2"
    sftp root@${HOST}:${DIR} <<< $REMOTE_CMD
}

remote_command () {
   # REMOTE_CMD="cd ${SITE_DIR};source ./venv/bin/activate;$1"
    ssh ${REMOTE_USER}@${HOST} $1 #$REMOTE_CMD
}

remote_root_command () {
    ssh root@${HOST} $1
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
    sshpass -p "$PASS" ssh root@$HOST 'ls' || { echo 'could not login as root'; echo 'try: sudo -s; passwd, or set "PermitRootLogin yes" in /etc/ssh/sshd_config' ; exit 1; }
    
    echo "Uploading pubilic SSH key for root"
    cd ~/.ssh/
    sshpass -p "$PASS" sftp root@$HOST:/root/.ssh/ <<< $'put id_rsa.pub'
    sshpass -p "$PASS" ssh root@$HOST 'rm -f /root/.ssh/authorized_keys'
    sshpass -p "$PASS" ssh root@$HOST 'mv /root/.ssh/id_rsa.pub  /root/.ssh/authorized_keys'
    
    echo "Uploading pubilic SSH key for remote user"
    sshpass -p "$REMOTE_PASS" sftp $REMOTE_USER@$HOST:/home/$REMOTE_USER/ <<< $'put id_rsa.pub'
    sshpass -p "$REMOTE_PASS" ssh $REMOTE_USER@$HOST "rm -f /home/$REMOTE_USER/.ssh/authorized_keys"
    sshpass -p "$REMOTE_PASS" ssh $REMOTE_USER@$HOST "mv /home/$REMOTE_USER/id_rsa.pub  /home/$REMOTE_USER/.ssh/authorized_keys"

    echo "Backing up original sshd config"
    sshpass -p "$PASS" ssh root@$HOST 'cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bk'
    
    echo "enabling pubkey authentication"
    sshpass -p "$PASS" ssh root@$HOST 'echo "PubKeyAuthentication yes" >> /etc/ssh/sshd_config'
    
    echo "Restarting remote ssh daemon"
    sshpass -p "$PASS" ssh root@${HOST} 'systemctl restart sshd' 
    
    # At this point we can use remote_root_command since we dont need sshpass
    # Do this step last so we don't lock ourselves out of the server if there is a problem
    #echo "Disabling password login"
    #remote_root_command "sed -i '/PasswordAuthentication yes/d' /etc/ssh/sshd_config"
    

    echo "Restarting remote ssh daemon"
    remote_root_command 'systemctl restart sshd' 
}

# Step 2 
SetupFirewall () {
    
    echo 'Setting up firewall'
    remote_root_command 'ufw allow 22' 
    remote_root_command 'ufw allow 80' 
    remote_root_command 'ufw allow 443' 
    #remote_root_command 'ufw allow 8080'
    remote_root_command 'systemctl enable ufw'
    remote_root_command 'ufw reload'
}


# Step 3
InstallDependencies () {
    
    echo "Updating server"
    remote_root_command 'apt update'
    remote_root_command 'apt -y upgrade'
    
    echo 'Installing packages'
    remote_root_command 'apt -y install apache2 libapache2-mod-wsgi-py3  python3.10-venv'
    
}


# Step 5
SetupDjangoServer () {
    
    echo "Setting up app ${APPDIR}"
    
    echo 'Cleaning local *.pyc files'
    find ${APPSRC}  -name '*.pyc'  -delete
    
    echo 'Cleaning remote'
    remote_root_command "rm -rf ${APPDIR}"
    
    echo 'Creating server dir'
    remote_root_command "mkdir $APPDIR"
    
    echo 'Uploading server source'
    #upload_file $APPDIR $APPSRC/scripts/sftp_upload_list.txt
    #upload_folder $APPDIR $APPSRC/db
    upload_folder $APPDIR $APPSRC/home
    upload_folder $APPDIR $APPSRC/loewetechsoftware_com
    upload_folder $APPDIR $APPSRC/logger
    upload_folder $APPDIR $APPSRC/scripts
    upload_folder $APPDIR $APPSRC/static
    upload_file $APPDIR $APPSRC/manage.py
    upload_file $APPDIR $APPSRC/requirements.txt
    

    echo 'setting permissions'
    remote_root_command "chown www-data:www-data -R ${APPDIR}"
    remote_root_command "chmod a+x ${APPDIR}"
    
}
 


# Step 5.1
SetupVenv () {
    echo "Creating virtual environment: $VENDIR"
    remote_root_command "python3 -m venv $VENDIR"
    
    echo 'Installing python packages'
    remote_root_command "source $VENDIR/bin/activate; pip install -r ${APPDIR}/requirements.txt"
    
    echo 'Setting permissions'
    remote_root_command "chown www-data:www-data -R $VENDIR"
}

# Step 6
InitDB () {
	
	echo "Deleting old database: $DBDIR"
	#remote_root_command "rm -rf $dbdir"
	#remote_root_command "mkdir $DBDIR"
	
    echo "Uploading database to remote host"
    #upload_file ${DBDIR}/ ${APPSRC}/db/logger.db
    
    echo 'Setting permissions on database'
    remote_root_command "chown www-data:www-data -R $DBDIR"
    remote_root_command "chmod a+rw ${DBDIR}/logger.db"
}

# Step 6 B
SetupPostgresql () {
	
	echo "Setting up Postgresql on $HOST"
}


# Step 7 
SetupApache () {
    
    echo 'Enabling WSGI mod'
    remote_root_command 'a2enmod wsgi'
    remote_root_command 'a2enmod ssl'
    
    #echo 'backing up apache default config and port.conf'
    #remote_root_command 'cp /etc/apache2/sites-enabled/000-default.conf /home/russell/'
    #remote_root_command 'cp /etc/apache2/ports.conf /etc/apache2/ports.conf.bk'
    
    echo 'Removing default config'
    remote_root_command 'rm -rf /etc/apache2/sites-enabled/*'
    
    echo 'Uploading apache conf file'
    #sftp root@$HOST:/etc/apache2/sites-enabled/ <<< $'put ${APPDIR}/loewelogger.conf'
    upload_file /etc/apache2/sites-enabled/ $APPSRC/loewelogger_http_dev.conf
    
    #echo 'Removing apache listing port 80'
    #remote_root_command "sed -i '/Listen 80/d' /etc/apache2/ports.conf"
    
    echo "Restarting apache"
    remote_root_command 'systemctl restart apache2'
    
}

CreateSSLCerts () {
    echo 'Creating self signed ssl certs'
    remote_root_command "rm -rf $SSLDIR"
    remote_root_command "mkdir $SSLDIR"
    remote_root_command "openssl req -x509 -newkey rsa:4096 -keyout $SSLDIR/key.pem -out ${SSLDIR}/cert.pem -sha256 -days 365"
    #remote_root_command "openssl genrsa -out $SSLDIR/server.key 1024"
    #remote_root_command "openssl req -new -key $SSLDIR/server.key -out $SSLDIR/server.csr"
    #remote_root_command "openssl x509 -req -days 366 -in $SSLDIR/server.csr -signkey $SSLDIR/server.key -out $SSLDIR/server.crt"
    #remote_root_command "openssl x509 -req -days 365 -in /etc/apache2/ssl/server.csr -signkey /etc/apache2/ssl/server.key -out /etc/apache2/ssl/server.crt"
    remote_root_command "chown www-data:www-data -R /etc/apache2/ssl"
}

# Step 8
SetupCertBot () {
    
    echo 'Setting up CertBot'
    remote_root_command  'apt-get -y install certbot python3-certbot-apache'
    
    echo 'Starting certbot'
    remote_root_command 'certbot certonly --standalone'
}

# Step 8b
UploadSSLCerts () {
    
    echo 'Creating folders'
    remote_root_command 'mkdir /etc/letsencrypt'
    remote_root_command 'mkdir /etc/letsencrypt/live'
    remote_root_command 'mkdir /etc/letsencrypt/live/loewetechsoftware.com'
    
    echo 'Uploading SSL certs to server'
    sftp root@$HOST:/etc/letsencrypt/live/loewetechsoftware.com/ <<< $'put /home/russell/Dropbox/ssl/ca_bundle.crt'
    sftp root@$HOST:/etc/letsencrypt/live/loewetechsoftware.com/ <<< $'put /home/russell/Dropbox/ssl/private.key'
    
    echo 'Renaming certs'
    remote_root_command 'cd /etc/letsencrypt/live/loewetechsoftware.com; mv ca_bundle.crt fullchain.pem; mv private.key privkey.pem'
}

# Step 9
StartApache () {
    
    echo 'Starting apache2 server'
    remote_root_command 'systemctl start apache2'
    remote_root_command 'systemctl restart apache2'
}

GetApacheErrorLogs () {

    echo '################## systemctl status apache2.service'  > ${APPSRC}/remote_errors.log
    remote_root_command 'systemctl status apache2.service'      >> ${APPSRC}/remote_errors.log
    
    echo '################## journalctl -xeu apache2.service'   >> ${APPSRC}/remote_errors.log
    remote_root_command 'journalctl -xeu apache2.service'       >> ${APPSRC}/remote_errors.log
    
    echo '################## /loewetechsoftware_com/server_errors.log' >> ${APPSRC}/remote_errors.log
    remote_root_command "cat ${APPDIR}/server_errors.log" >> ${APPSRC}/remote_errors.log
}


ParseCommand () {
while getopts ":hjpabds" opt; do
        case ${opt} in
    h|\?)
      echo "-j       ./src js source files and build (no restart)"
      echo "-p       set node production env and run node"
      echo "-d       set node to development mode and run"
      echo "-a       Archive to Dropbox"
      echo "-b       initDB"
      exit 1
      ;;
    j) loadJs ;;
    p) Prod ;;
    d) Dev ;;
    a) gitArchive /home/russell/ loewetechsoftware_com;;
    s) StartIPs;;
    b) initDB;;
     *) echo "Unknown option" 
        break   ;;
  esac
done
}

echo $HOST
#InitSSHKeys
###SetupFirewall
#InstallDependencies
SetupDjangoServer
#SetupVenv
#InitDB
#SetupPostgresql
#SetupApache
###CreateSSLCerts
#####SetupCertBot
#####UploadSSLCerts
StartApache
GetApacheErrorLogs
exit 0
