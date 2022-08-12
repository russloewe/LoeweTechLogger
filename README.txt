#Installation

## Option 1 Install Remotely with SSH

### Setup Environment variables

First, the variables that both the setup script and the Django app require
are defined in the environment file:

		loewetechsoftware_com/loewetechsoftware_com/.env

The initial .env file will need to be filled out fresh from the repo.
The variables are:

##### SECRET_KEY

Used by the django app. use long, random string

##### EMAIL_HOST_PASSWORD + EMAIL_HOST_USER

The login username and password for the email service. This is currently
Zoho.

##### PASS

Root password for remote server.

##### REMOTE_USER + REMOTE_PASS

Password and username for remote server.

##### DBDIR

Directory where sqlite3 database file will be stored on the remote server
when sqlite3 is used as the database backend.

##### VENDIR

Directory where python3 virtual environment will be on the remote server. 
Do not us a sub directory of the app folder or updates to the server's code
will wipe the database. Recomend using /var/db_loewetech

##### APPSRC
##### APPDIR
##### HOST
##### SSLDIR

##Setup database

###Option 1: sqlite
use a local sqlite database. Setup the database with the command


	./manage.py migrate

###Option 2: Setup Postrgesql server
The details for the postgre server are in docker-compase.yaml
Run the commands to start the server:

    ./docker_compose pull
    ./docker_compuse up



## Backup sqlite database weekly on Sunday at midnight cron line :

    0 0 * * 0 /home/russell/Dropbox/loewetechsoftware_com/scripts/backup_sqlite_db.sh  2>&1 > /home/russell/Dropbox/loewetechsoftware_com/db/backup_db.log
