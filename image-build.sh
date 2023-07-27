#!/bin/sh

. ./image-env.sh

podman build -f Containerfile -t ${PROJECT_ID}:${GIT_HASH} .

podman tag ${PROJECT_ID}:${GIT_HASH} ${PROJECT_ID}:${VERSION}

