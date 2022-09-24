# About 

This is an open source web app for logging Type 1 Diabetes numbers.

# Project Goals:



- **Free**, I started this because I couldn't find a quality app that wasn't limited for free use.
- **Simple**, The platform needs to be as bare bones as possible while still serving it's functions.
- **Low Maintence**, Use as few libraries as possible to reduce maintance labor.


# Installation

This project has been deveploped to run on Ubuntu server. The project is based on Django, so it could theoretically run anywhere. However, other OS's might not have compatible Python libraries that this project depends on. 

To install first open ./loewetechsoftware_com/.env and fill out the following variables:

	SECRET_KEY= {random string about 50 chars}
	EMAIL_HOST_PASSWORD= { backend email router, we use zoho.com}
	EMAIL_HOST_USER=
	PASS= {remote server's root pass}
	DBDIR=/var/db_logger {remote server's path for sqlite db}
	VENDIR=/var/venv_logger {remote path for virtural python environment}
	APPSRC=/home/russell/Dropbox/loewetechsoftware_com { local workstatoin absolute path where source is download}
	APPDIR=/var/loewetechsoftware_com {remote path to django app source}
	HOST={domain name for remote server}
	TWILIO_ACCOUNT_SID=
	TWILIO_AUTH_TOKEN=

Then open ./load.sh in the project root, and uncomment the following lines if not already:
	
	
	InitSSHKeys
	SetupFirewall
	InstallDependencies
	SetupDjangoServer
	SetupVenv
	InitDB
	SetupPostgresql
	SetupApache
	SetupCertBot
	GetApacheErrorLogs

Then execute ./load.sh 
