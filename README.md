# LoeweTechLogger
A MVC logging web app for Type 1 Diabetes

## Environment

    Ubuntu 18.04, Django3, Python3, 

## create virtual environment

    python3 -m venv ./venv
    source ./venv/bin/activate
    pip install "django>=3.1"
    pip install "psycopg2>=2.8,<2.9"
    pip3 install pytz psycopg2
    pip3 install django-bootstrap-static

## Backup sqlite database weekly on Sunday at midnight cron line :

    0 0 * * 0 /home/russell/Dropbox/loewetechsoftware_com/scripts/backup_sqlite_db.sh > /home/russell/Dropbox/loewetechsoftware_com/scripts/cron-logs/backup_sqlite_db.log
    
## Install

add: 
    
         path('logger/', include('logger.urls')),

to urls.py in app folder.
    
    
add:
    
        ./loewelogger_apache2.conf
        
to site-enabled apache2 folder. See comments in the logger for 
apach2 dependecies, but in short, install wsgi_mod with a2enmod

add:

        ./logger 
to a Django root folder. 
    
see:
    
        https://docs.djangoproject.com/en/3.0/intro/install/#
        
on how to get a Django web app installed.
    
## Dependencies

    Django>=2.0,<3.0
    psycopg2>=2.7,<3.0 

