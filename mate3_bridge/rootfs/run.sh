#!/usr/bin/with-contenv bashio

INTERFACE=$(bashio::config "interface")
DEBUG=$(bashio::config "debug")
PORT=$(bashio::config "port")
MQTT_HOST=$(bashio::config "mqtt_host")
MQTT_PORT=$(bashio::config "mqtt_port")
MQTT_USERNAME=$(bashio::config "mqtt_username")
MQTT_PASSWORD=$(bashio::config "mqtt_password")
DISCOVERY=$(bashio::config "discovery")
OTHER_ARGS=""

if [ "$DEBUG" = true ] ; then
    OTHER_ARGS="${OTHER_ARGS} --debug"
fi

echo "Starting mate3_bridge.py"
python3 -u /mate3_bridge.py $OTHER_ARGS --interface $INTERFACE --port $PORT \
                            --host $MQTT_HOST --hostport $MQTT_PORT \
                            --username $MQTT_USERNAME --password $MQTT_PASSWORD \
                            --discovery $DISCOVERY
                            