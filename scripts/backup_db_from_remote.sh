#!/bin/bash

# Load variables from env file:
# 	HOST
#	DBDIR
#	APPSRC
#	APPDIR
source ../loewetechsoftware_com/.env

today=$(date +"%Y-%m-%d")

echo "$today $HOST : $DBDIR/logger.db -> $APPSRC/db_backups/logger_backup_${today}.db"

# download database
sftp root@$HOST:$DBDIR <<< $"get logger.db ${APPSRC}/db_backups/logger_backup_${today}.db"

# optional download to source working db
#sftp root@$HOST:$APPDIR/db/ <<< $"get logger.db ${APPSRC}/db/logger.db"
