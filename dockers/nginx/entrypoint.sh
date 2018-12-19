#!/bin/bash

if [ ! -e "/etc/nginx/external/server-key.pem" ] || [ ! -e "/etc/nginx/external/server-cert.pem" ]
then
   echo ">> GENERATING NEW KEYS"
   bash /opt/auto-generate-certs.sh
fi

DH_PREGEN="/dh.pem"
if [ -f "$DH_PREGEN" ]
then
    mv /dh.pem /etc/nginx/external/
fi

if [ -z ${DH_SIZE+x} ]
then
  >&2 echo ">> no \$DH_SIZE specified using default" 
  DH_SIZE="2048"
fi


DH="/etc/nginx/external/dh.pem"

if [ ! -e "$DH" ]
then
  echo ">> seems like the first start of nginx"
  echo ">> generating $DH with size: $DH_SIZE"
  openssl dhparam -out "$DH" $DH_SIZE
fi

chmod 440 /etc/nginx/external/*

echo ">> exec docker CMD"
echo "$@"
exec "$@"

