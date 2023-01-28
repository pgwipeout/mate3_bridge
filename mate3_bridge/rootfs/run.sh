#!/usr/bin/with-contenv bashio

INTERFACE=$(bashio::config "interface")
DEBUG=$(bashio::config "debug")
PORT=$(bashio::config "port")

if [ "$DEBUG" = true ] ; then
OTHER_ARGS="${OTHER_ARGS} --debug"

echo "Starting mate3_bridge.py"
python3 -u /mate3_bridge.py $OTHER_ARGS --interface $INTERFACE --port $PORT