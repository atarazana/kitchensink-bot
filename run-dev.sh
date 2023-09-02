#!/bin/sh

OC_USER=$(oc whoami)
OC_TOKEN=$(oc whoami -t)

if [ -z "${OC_TOKEN}" ]
then
    echo "You have to log in the OpenShift cluster and have cluster-admin permissions"
    exit 1
fi

# export $(grep -v '^#' .env | xargs)
export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst)

echo "DEV_USERNAME=${DEV_USERNAME}"

python app.py