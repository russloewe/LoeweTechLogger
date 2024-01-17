#! /bin/bash

# >crontab -e
## m h  dom mon dow   command
#  1 1  *   *   *     /home/russell/Dropbox/loewetechsoftware_com/backup_db.sh >> /home/russell/backup_loewetech.log 2>&1

# Load environment variables from ./loewetechsoftware_com/.env
source ./loewetechsoftware_com/.env

echo "APPSRC=$APPSRC"
echo "APPDIR=$APPDIR"
echo "HOST=$HOST"

# Check if any of the variables are null
if [[ -z $APPSRC || -z $APPDIR || -z $HOST ]]; then
  echo "Error: One or more variables are null."
  exit 1
else
  echo "All variables found."
fi

echo "Downloading $DB_NAME to $APPSRC/$DB_NAME.sql"
ssh root@${HOST} "sudo -u postgres pg_dump $DB_NAME" > $APPSRC/$DB_NAME.sql

echo "...Done"
exit 0
