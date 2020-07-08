# LoeweTechLogger
A MVC logging web app for Type 1 Diabetes

## Environment

    Ubuntu 18.04, Django2, Python3, Javascript, HTML5, CSS3

## Install

add: 
    
         path('logger/', include('logger.urls')),

to urls.py in app folder.
    
    
add:
    
        ./loewelogger.conf
        
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

