# Misc

## Dose calculation

The dose calculation uses rates determined by the patients dose object. 
The actual calculation is done by javascript functions defined in 

		./logger/templates/logger/scripts/dose_helper.html
		
Dose corrections base on CGM arrows are determined by figure 4.3 of 

	"A Practical Approach to Using Trend Arrows on the Dexcom G5 CGM System for the Management of Adults With Diabetes"

of Journal of the Endocrine Society (Aleppo). [pubmed.ncbi.nlm.nih.gov/29344577](https://pubmed.ncbi.nlm.nih.gov/29344577/)

#Installation


## Setup Environment variables

First, the variables that both the setup script and the Django app require
are defined in the environment file:

		loewetechsoftware_com/loewetechsoftware_com/.env

The initial .env file will need to be filled out fresh from the repo.
The variables are:

##### SECRET_KEY

Used by the django app. use long, random string


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

## Setup Virtual Environment

Setup a virtual environment with:

        ./python3 -m venv venv

then from the base path activate and install modules:

        source /path/to/venv/bin/activate
        pip install -r requirements.

## Setup database

###Option 1: sqlite

To use a local sqlite database make sure this variable in the .env file
    
    USE_POSTGRESQL=False 
    
Then setup the database with the command

	./manage.py migrate

###Option 2: Setup Postrgesql server

The details for the postgre server are in docker-compase.yaml
Run the commands to start the server:

    ./docker_compose pull
    ./docker_compuse up

setup postgresql to us password authentication add this line to 
pg_hba.cong in postgresql etc folder:

# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             loewetechsoftware                           md5


create a new database user    

    sudo -u postgres createuser loewetechsoftware
    
update password

    sudo -u postgres psql
    ALTER USER loewetechsoftware WITH PASSWORD 'new_password';

## Backup sqlite database weekly on Sunday at midnight cron line :

    0 0 * * 0 /home/russell/Dropbox/loewetechsoftware_com/scripts/backup_sqlite_db.sh  2>&1 > /home/russell/Dropbox/Docs/backup_db.log

## Backup Postgresql database 


    sudo -u postgres pg_dumpall > backup_filename.sql

    sudo -u postgres pg_dump loewetechsoftware > loewetechsoftware.sql

## Restore Postgresql Database

    createdb loewetechsoftware
    pg_restore -U loewetechsoftware -d loewetechsoftware /home/russell/Dropbox/loewetechsoftware_com/loewetechsoftware.sql
    psql -U loewetechsoftware -d loewetechsoftware -f loewetechsoftware.sql

Verify with 

    psql -U your_username -d your_database_name


## Get SSL Certificate

First, shutdown the apache2 server. Then run this:

		certbot certonly --standalone
        
then restart the apache2 server. It should download the certificate files to path specified in the apache .conf file. 
If not make sure the path in the conf file matches where the certbot downloaded the ssl files.

# Citations

Aleppo G, Laffel LM, Ahmann AJ, Hirsch IB, Kruger DF, Peters A, Weinstock RS, Harris DR. A Practical Approach to Using Trend Arrows on the Dexcom G5 CGM System for the Management of Adults With Diabetes. J Endocr Soc. 2017 Nov 20;1(12):1445-1460. doi: 10.1210/js.2017-00388. PMID: 29344577; PMCID: PMC5760210.
