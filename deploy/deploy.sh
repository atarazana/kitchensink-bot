#!/bin/sh

ENV_FILE=../.env.deploy

if ! test -f "${ENV_FILE}"; then
    echo "${ENV_FILE} does not exist."
    exit 1
fi

. ${ENV_FILE}

# TODO Change by replace...
REGISTRY=$(oc get route myregistry-quay -n quay-system -o jsonpath='{.spec.host}')
export CONTAINER_REGISTRY_USERNAME="${DEV_USERNAME}+cicd"
echo "CONTAINER_REGISTRY_PASSWORD: " && read -s CONTAINER_REGISTRY_PASSWORD

printf "\nREGISTRY=%s\nCONTAINER_REGISTRY_USERNAME=%s\nCONTAINER_REGISTRY_PASSWORD=%s" "${REGISTRY}" "${CONTAINER_REGISTRY_USERNAME}" "${CONTAINER_REGISTRY_PASSWORD}" >> ${ENV_FILE}

oc new-project kitchensink-bot

oc delete secret kitchensink-bot-env -n kitchensink-bot
oc create secret generic kitchensink-bot-env --from-env-file=${ENV_FILE} -n kitchensink-bot

oc apply -n kitchensink-bot -f deploy.yaml