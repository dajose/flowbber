#!/usr/bin/env bash

set -o errexit
set -o nounset

###############
# Supervisord #
###############

supervisord -c /etc/supervisor/supervisord.conf

###############
# InfluxDB    #
###############

# Wait for influxd
echo -n "[Entrypoint] Waiting for influxd ..."
while ! influx -execute "SHOW DATABASES;" > /dev/null 2>&1; do
    echo -n "."; sleep 0.2
done
echo ""

echo "[Entrypoint] Creating influxdb databases ..."
influx -execute 'CREATE DATABASE flowbber;'
influx -execute 'CREATE DATABASE cpud;'
influx -execute 'CREATE DATABASE speedd;'

###############
# MongoDB     #
###############

# Wait for mongod
echo -n "[Entrypoint] Waiting for mongod ..."
while ! mongo --eval "db.version()" > /dev/null 2>&1; do
    echo -n "."; sleep 0.2
done
echo ""


exec /usr/local/bin/docker-entrypoint $@
