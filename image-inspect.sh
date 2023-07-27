#!/bin/sh

. ./image-env.sh

skopeo inspect docker://$REGISTRY/$REGISTRY_USER_ID/${PROJECT_ID}:${VERSION} | jq -r .Digest
