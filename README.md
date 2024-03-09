# Installation

This app is developed and deployed on ubuntu servers. 

## Setup Firewall

Enable the Ubuntu Server firewall with these UFW commands. 
Only ports 80, 443 accept public connections. 
Port 9494 is for the development server and only accepts local network connections.

    remote_command 'ufw allow from 10.0.0.0/24 to any port 22 proto tcp' 
    remote_command 'ufw allow 80' 
    remote_command 'ufw allow 443' 
    remote_command 'ufw allow from 10.0.0.0/24 to any port 9494 proto tcp'
    remote_command 'systemctl enable ufw'
    remote_command 'ufw reload'

## Setup Environment variables

The variables that both the setup script and the Django app require
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

##### VENDIR

Directory where python3 virtual environment will be on the remote server. 



## Setup Virtual Environment

Use the path specified by VENDIR in the .env file. Default 'loewetech'.
Setup a virtual environment with:

        ./python3 -m venv /var/venv/loewetech

then from the base path activate and install modules:

        source /var/venv/loewetech/bin/activate
        pip install -r requirements.

## Setup database

Use Postgresql database server.
Don't start with the local sqlite3 database.
You'll have to migrate eventually so just usq PostgreSQL from git-go.

### New Database

Create a new database from the command line with creatdb

    sudo -u postgres creatdb loewetechsoftware
    
createdb is a command line tool, NOT an sql command in psql.

setup postgresql to us password authentication add this line to 
pg_hba.cong in postgresql etc folder:

    # TYPE  DATABASE        USER            ADDRESS                 METHOD
    local   all             loewetechsoftware                           md5


create a new database user    

    sudo -u postgres createuser loewetechsoftware
    
update password

    sudo -u postgres psql
    ALTER USER loewetechsoftware WITH PASSWORD 'new_password';

if there are issues with permissions make sure the user has the right permissions 
for the database:

    GRANT ALL PRIVILEGES ON DATABASE loewetechsoftware TO loewetechsoftware;


### Backup Postgresql database 

Run these commands directly on host server

    sudo -u postgres pg_dumpall > backup_filename.sql

    sudo -u postgres pg_dump loewetechsoftware > loewetechsoftware.sql

### Restore Postgresql Database

    createdb loewetechsoftware
    psql -U loewetechsoftware -d loewetechsoftware -f loewetechsoftware.sql


## Get SSL Certificate

Shutdown the apache2 server.

        systemctl stop apache2

Then run this:

		certbot certonly --standalone
        
Then restart apache server

        systemctl start apache2

It should download the certificate files to path specified in the apache .conf file. 
If not make sure the path in the conf file matches where the certbot downloaded the ssl files.

# Misc

## Dose calculation

The dose calculation uses rates determined by the patients dose object. 
The actual calculation is done by javascript functions defined in 

		./logger/templates/logger/scripts/dose_helper.html
		
Dose corrections base on CGM arrows are determined by figure 4.3 of 

	"A Practical Approach to Using Trend Arrows on the Dexcom G5 CGM System for the Management of Adults With Diabetes"

of Journal of the Endocrine Society (Aleppo). [pubmed.ncbi.nlm.nih.gov/29344577](https://pubmed.ncbi.nlm.nih.gov/29344577/)

# Citations

Aleppo G, Laffel LM, Ahmann AJ, Hirsch IB, Kruger DF, Peters A, Weinstock RS, Harris DR. A Practical Approach to Using Trend Arrows on the Dexcom G5 CGM System for the Management of Adults With Diabetes. J Endocr Soc. 2017 Nov 20;1(12):1445-1460. doi: 10.1210/js.2017-00388. PMID: 29344577; PMCID: PMC5760210.
