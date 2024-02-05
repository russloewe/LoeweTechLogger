# Settings

The settings and wsgi files are split into three different files:

#### wsgi.py / settings.py
    
This is for running the server on the local deveplopment machine while connecting to the production database from a local network.

#### wsgi_prod.py / settings_prod.py

This is for the main production server facing the public internet

#### wsgi_admin.py / settings_admin.py

This is for the main production server facing a local network to allow access to Django admin panel
