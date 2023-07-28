#!/bin/sh

ENV_FILE=../.env.deploy

if ! test -f "${ENV_FILE}"; then
    echo "${ENV_FILE} does not exist."
    exit 1
fi

. ${ENV_FILE}

oc new-project kitchensink-bot

oc delete secret kitchensink-bot-env -n kitchensink-bot
oc create secret generic kitchensink-bot-env --from-env-file=${ENV_FILE} -n kitchensink-bot

oc apply -n kitchensink-bot -f deploy.yaml