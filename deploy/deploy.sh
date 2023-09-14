#!/bin/sh

DEPLOYMENT_NS=kitchensink-bot
ENV_FILE="../.env.deploy"

if ! test -f "${ENV_FILE}"; then
    echo "${ENV_FILE} does not exist."
    exit 1
fi

. ${ENV_FILE}

oc new-project ${DEPLOYMENT_NS}

oc delete secret kitchensink-bot-data -n ${DEPLOYMENT_NS}
oc create secret generic kitchensink-bot-data --from-file=../data -n ${DEPLOYMENT_NS}

oc delete secret kitchensink-bot-env -n ${DEPLOYMENT_NS}
oc create secret generic kitchensink-bot-env --from-env-file=${ENV_FILE} -n ${DEPLOYMENT_NS}

oc apply -n ${DEPLOYMENT_NS} -f deploy.yaml

oc start-build bc/kitchensink-bot -n ${DEPLOYMENT_NS}