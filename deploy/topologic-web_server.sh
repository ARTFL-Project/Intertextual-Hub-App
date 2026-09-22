#!/bin/sh
# The embedded TopoLogic API server. Deployment-specific, because upstream's copy defaults
# to PORT=80 and this container proxies to 8443.
#
# No TLS: upstream's own script already takes the plain-HTTP branch when KEYFILE is empty,
# and this deployment had filled it in with the host's live private key. Logs go to stdout.
#
# This is the embedded TopoLogic, pinned to TopoLogic@91e2e210 (2020-11-03) with its library
# at @b4d3b446. It is NOT the standalone `topologic` service, whose upstream has since been
# rewritten on DuckDB and cannot read this service's PostgreSQL model tables.
exec gunicorn \
    -k uvicorn.workers.UvicornWorker \
    -b 127.0.0.1:8443 \
    -w 4 \
    --access-logfile - \
    --error-logfile - \
    --chdir /var/lib/topologic/api/ \
    topologic_explorer:app
