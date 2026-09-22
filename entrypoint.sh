#!/bin/sh
# intertextual-hub: start PostgreSQL, both gunicorn apps and Apache, and shut them all
# down cleanly on SIGTERM. Nothing here runs as root — there is no gosu and no privilege
# drop, unlike the VM-era entrypoint this replaces.
set -e

# Apache wants these writable, and the root filesystem is not. They live on the tmpfs.
mkdir -p "$APACHE_RUN_DIR" "$APACHE_LOCK_DIR" "$APACHE_LOG_DIR"

# listen_addresses empty: the database speaks only over the socket in /tmp. There is no
# TCP listener at all, so a compromise of any of the three web tiers cannot reach it over
# the network — and every psycopg2.connect() in this application must therefore find it
# through PGHOST rather than an explicit host="localhost".
# Production's tuning, carried across rather than inherited from initdb's defaults. Not a
# tuning exercise: the old cluster runs shared_buffers=8GB and work_mem=24MB, and a fresh
# initdb gives 128MB and 4MB. Leaving those at the defaults made staging 19% slower with a
# p95 1.4x production's - a regression introduced by omission, which T6 is what catches.
#
#   shared_buffers        8GB    64x the default. Counted against mem_limit (shared memory).
#   effective_cache_size  8GB    planner hint only, no allocation.
#   work_mem             24MB    6x the default; the alignment queries sort.
#   maintenance_work_mem 64MB    as deployed.
#   max_wal_size          1GB / min_wal_size 80MB   as deployed.
pg_ctl -D "$PGDATA" -w start -o "-c unix_socket_directories=/tmp -c listen_addresses='' \
  -c shared_buffers=8GB \
  -c effective_cache_size=8GB \
  -c work_mem=24MB \
  -c maintenance_work_mem=64MB \
  -c max_wal_size=1GB \
  -c min_wal_size=80MB"

hub_pid=""; topo_pid=""; httpd_pid=""

shutdown() {
  # Apache first, so nothing new arrives while the apps are going away.
  [ -n "$httpd_pid" ] && kill -TERM "$httpd_pid" 2>/dev/null || true
  [ -n "$hub_pid" ]   && kill -TERM "$hub_pid"   2>/dev/null || true
  [ -n "$topo_pid" ]  && kill -TERM "$topo_pid"  2>/dev/null || true
  wait "$httpd_pid" "$hub_pid" "$topo_pid" 2>/dev/null || true
  # Without this every restart is a crash recovery, and the weekly rebuild would pay it
  # every Sunday.
  pg_ctl -D "$PGDATA" -m fast -w stop || true
  exit 0
}
trap shutdown TERM INT

sh /var/lib/topologic/api_server/web_server.sh & topo_pid=$!
sh /var/www/html/intertextual_hub/Intertextual-Hub-App/api_server/web_server.sh & hub_pid=$!
apache2ctl -D FOREGROUND & httpd_pid=$!

# Nothing else supervises any of this. Apache is the front door, so if a gunicorn dies the
# site keeps answering — with 502s on most of itself — and a port check would call that
# healthy. That is the failure mode the old `GET /` probe could not see and it is why the
# healthcheck in the compose file reaches all three tiers.
#
# Here the watchdog only has to notice and exit; `restart: unless-stopped` does the rest.
down() { echo "entrypoint: $1 is gone; exiting for restart" >&2; shutdown; }
while :; do
  sleep 15
  kill -0 "$httpd_pid" 2>/dev/null || down "apache"
  kill -0 "$hub_pid"   2>/dev/null || down "the intertextual-hub app"
  kill -0 "$topo_pid"  2>/dev/null || down "the topologic app"
  # -U postgres -d postgres matters: a bare pg_isready connects as the OS user, uid 483,
  # which is not a role in this cluster. It still exits 0 — the server answered, which is
  # all it asks — but the server logs a FATAL every 15 seconds forever, and a log full of
  # harmless FATALs is how people learn to ignore real ones.
  pg_isready -q -U postgres -d postgres \
    || { sleep 5; pg_isready -q -U postgres -d postgres || down "postgres"; }
done
