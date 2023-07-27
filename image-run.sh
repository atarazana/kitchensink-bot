#!/bin/sh

. .env

. ./image-env.sh

# --entrypoint bash \

podman run -it --rm -p 8080:8080 \
  -e SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN} \
  -e SLACK_SIGNING_SECRET=${SLACK_SIGNING_SECRET} \
  -e SLACK_APP_TOKEN=${SLACK_APP_TOKEN} \
  -e DATA_DIR=/deployments/data \
  -e DB_DIR=/deployments \
  -e DEV_USERNAME=${DEV_USERNAME} \
  -e DEV_PASSWORD=${DEV_PASSWORD} \
  -e PROJECT_NAME=${PROJECT_NAME} \
  -e FRUIT_SERVICE_APP_NAME=${FRUIT_SERVICE_APP_NAME} \
  -e FRUIT_GATEWAY_APP_NAME=${FRUIT_GATEWAY_APP_NAME} \
  -e SLACK_WEBHOOK=${SLACK_WEBHOOK} \
  -e SLACK_CHANNEL=${SLACK_CHANNEL} \
  -e REPOSITORY=${REPOSITORY} \
  -e TAG=${TAG} \
  -e REGISTRY=${REGISTRY} \
  -e CONTAINER_REGISTRY_USERNAME=${CONTAINER_REGISTRY_USERNAME} \
  -e CONTAINER_REGISTRY_PASSWORD=${CONTAINER_REGISTRY_PASSWORD} \
  -e KUBECONFIG=/var/kubeconfig/config \
  --volume kubeconfig:/var/kubeconfig \
  --entrypoint bash \
  --user 1234 \
  --name bot localhost/kitchensink-bot:${VERSION}

