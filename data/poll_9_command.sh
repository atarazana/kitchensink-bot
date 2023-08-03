printf "=================\nEXECUTING STEP %s\n=================\n" "01"

GITEA_HOST="$(oc get route repository -n gitea-system -o jsonpath='{.spec.host}')"
echo "GITEA_HOST=${GITEA_HOST}"

ARGOCD_HOST="$(oc get route openshift-gitops-server -n openshift-gitops -o jsonpath='{.spec.host}')"
echo "ARGOCD_HOST=${ARGOCD_HOST}"

ARGOCD_USERNAME=admin
ARGOCD_PASSWORD=$(oc get secret openshift-gitops-cluster -o jsonpath='{.data.admin\.password}' -n openshift-gitops | base64 -d)

argocd login $ARGOCD_HOST --insecure --grpc-web --username ${ARGOCD_USERNAME} --password ${ARGOCD_PASSWORD}

GIT_PAT=$(curl -k -s -XPOST -H "Content-Type: application/json" \
  -d '{"name":"cicd'"${RANDOM}"'","scopes": ["repo"]}' \
  -u ${DEV_USERNAME}:openshift \
  https://${GITEA_HOST}/api/v1/users/${DEV_USERNAME}/tokens | jq -r .sha1)
echo "GIT_PAT=${GIT_PAT}"

BASE_DIR=/tmp/${DEV_USERNAME}

mkdir ${BASE_DIR} && cd ${BASE_DIR}

git clone https://${DEV_USERNAME}:openshift@${GITEA_HOST}/${DEV_USERNAME}/kitchensink ${BASE_DIR}/kitchensink
git clone https://${DEV_USERNAME}:openshift@${GITEA_HOST}/${DEV_USERNAME}/kitchensink-conf ${BASE_DIR}/kitchensink-conf

git -C ${BASE_DIR}/kitchensink config --local user.email "${DEV_USERNAME}@ocp.com"
git -C ${BASE_DIR}/kitchensink config --local user.name "${DEV_USERNAME}"
git -C ${BASE_DIR}/kitchensink-conf config --local user.email "${DEV_USERNAME}@ocp.com"
git -C ${BASE_DIR}/kitchensink-conf config --local user.name "${DEV_USERNAME}"

if [ "$(uname)" == "Darwin" ]; then
  sed -i '' 's|# configure_drivers ${injected_dir}/driver-postgresql.env|configure_drivers ${injected_dir}/driver-postgresql.env|g' ${BASE_DIR}/kitchensink/extensions/install.sh
else
  sed -i 's|# configure_drivers ${injected_dir}/driver-postgresql.env|configure_drivers ${injected_dir}/driver-postgresql.env|g' ${BASE_DIR}/kitchensink/extensions/install.sh
fi

yq e -i '.kitchensinkBuilderImage = "jboss-eap74-openjdk8-openshift:7.4.0"' ${BASE_DIR}/kitchensink-conf/cicd/values.yaml

git -C ${BASE_DIR}/kitchensink-conf commit -a -m "from poll_9.sh"
git -C ${BASE_DIR}/kitchensink-conf push origin main

ARGOCD_APP_NAME=openshift-gitops/kitchensink-cicd-${DEV_USERNAME}
# WAIT_FOR_HEALTH_FLAG="--health"
argocd --grpc-web app get --refresh ${ARGOCD_APP_NAME} > /dev/null && \
argocd --grpc-web app wait ${ARGOCD_APP_NAME} --sync ${WAIT_FOR_HEALTH_FLAG}

git -C ${BASE_DIR}/kitchensink commit -a -m "from poll_9.sh"
git -C ${BASE_DIR}/kitchensink push origin main

rm -rf  ${BASE_DIR}

