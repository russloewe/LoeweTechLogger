
## Setup Postrgesql server
The details for the postgre server are in docker-compase.yaml
Run the commands to start the server:

    ./docker_compose pull
    ./docker_compuse up

## create virtual environment

    python3 -m venv ./venv
    source ./venv/bin/activate
    pip install "django>=2.2,<3"
    pip install "psycopg2>=2.8,<2.9"
    pip3 install pytz psycopg2
    pip3 install django-bootstrap-static

## Compute integrity checksum

    openssl dgst -sha384 -binary FILENAME.js | openssl base64 -A

## Backup sqlite database weekly on Sunday at midnight cron line :

    0 0 * * 0 /home/russell/Dropbox/loewetechsoftware_com/scripts/backup_sqlite_db.sh > /home/russell/Dropbox/loewetechsoftware_com/scripts/cron-logs/backup_sqlite_db.log
