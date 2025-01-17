#!/bin/sh

# Define the number of workers for your app. Between 4 and 12 should be fine.
WORKERS=4

# Define on which port the webserver will be listening. If you have a webserver already listening to port 80
# you should proxy requests to below port to the app
PORT=8444

# If using an https connection (you should), define your SSL keys and certificate locations here
KEYFILE=/etc/letsencrypt/live/anomander.uchicago.edu/privkey.pem
CERTFILE=/etc/letsencrypt/live/anomander.uchicago.edu/fullchain.pem

gunicorn --keyfile=$KEYFILE --certfile=$CERTFILE -k uvicorn.workers.UvicornWorker -b :$PORT -w 4 --access-logfile=/var/www/html/intertextual_hub/Intertextual-Hub-App/api_server/access.log --error-logfile=/var/www/html/intertextual_hub/Intertextual-Hub-App/api_server/error.log --chdir /var/www/html/intertextual_hub/Intertextual-Hub-App/api/ main:app
