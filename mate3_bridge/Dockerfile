# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM=homeassistant/amd64-base-python:3.9-alpine3.16
FROM ${BUILD_FROM} as builder

# Copy root filesystem
COPY rootfs /
RUN \
    chmod a+x /run.sh

CMD {"/run.sh"}
