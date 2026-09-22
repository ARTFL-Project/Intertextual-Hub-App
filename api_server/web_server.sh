#!/bin/sh

# Define the number of workers for your app. Between 4 and 12 should be fine.
WORKERS=4

# Define on which port the webserver will be listening. A webserver in front of this one
# proxies to it.
PORT=8444

# No TLS here. This process speaks plain HTTP on the loopback interface and the Apache in
# front of it is the only thing that terminates TLS.
#
# It used to hold --keyfile and --certfile of its own, reading the host's live Let's Encrypt
# key directly, which is why /etc/letsencrypt was bind-mounted read-write into a container
# running a web application. Both gunicorn apps did it, and the container's own Apache did it
# a third time. Removing it here is half of that change; the other half is the Apache
# configuration, and the two have to move together or the site returns 502.
#
# Logs go to stdout and stderr so the container runtime owns rotation. They used to be
# written to files inside the container, where the Apache access log reached 9.9 GB because
# logrotate is driven by cron and nothing starts cron in a container.

exec gunicorn \
    -k uvicorn.workers.UvicornWorker \
    -b 127.0.0.1:$PORT \
    -w $WORKERS \
    --access-logfile - \
    --error-logfile - \
    --chdir /var/www/html/intertextual_hub/Intertextual-Hub-App/api/ \
    main:app
