printf "\n=================\nEXECUTING STEP %s\n=================\n" "01"

printf "=> whoami: %s\n" "$(whoami)"
printf "=> oc whoami: %s\n" "$(oc whoami)"

GITEA_HOST="$(oc get route repository -n gitea-system -o jsonpath='{.spec.host}')"
echo "GITEA_HOST=${GITEA_HOST}"

ARGOCD_HOST="$(oc get route openshift-gitops-server -n openshift-gitops -o jsonpath='{.spec.host}')"
echo "ARGOCD_HOST=${ARGOCD_HOST}"

ARGOCD_USERNAME=admin
ARGOCD_PASSWORD=$(oc get secret openshift-gitops-cluster -o jsonpath='{.data.admin\.password}' -n openshift-gitops | base64 -d)

printf "=> About to log in argocd with user: %s and pass: %s\n" "${ARGOCD_USERNAME}" "${ARGOCD_PASSWORD}"

argocd login $ARGOCD_HOST --insecure --grpc-web --username ${ARGOCD_USERNAME} --password ${ARGOCD_PASSWORD}

GIT_PAT=$(curl -k -s -XPOST -H "Content-Type: application/json" \
  -d '{"name":"cicd'"${RANDOM}"'","scopes": ["repo"]}' \
  -u ${DEV_USERNAME}:openshift \
  https://${GITEA_HOST}/api/v1/users/${DEV_USERNAME}/tokens | jq -r .sha1)

printf "=> GIT_PAT: %s\n" "${GIT_PAT}"

BASE_DIR=/tmp/${DEV_USERNAME}

printf "=> About to make dir: %s\n" "${BASE_DIR}"

mkdir ${BASE_DIR} && cd ${BASE_DIR}

printf "=> Cloning %s in %s\n" "https://${DEV_USERNAME}:openshift@${GITEA_HOST}/${DEV_USERNAME}/kitchensink\n" "${BASE_DIR}/kitchensink"
git clone https://${DEV_USERNAME}:openshift@${GITEA_HOST}/${DEV_USERNAME}/kitchensink ${BASE_DIR}/kitchensink
printf "=> Cloning %s in %s\n" "https://${DEV_USERNAME}:openshift@${GITEA_HOST}/${DEV_USERNAME}/kitchensink\n" "${BASE_DIR}/kitchensink"
git clone https://${DEV_USERNAME}:openshift@${GITEA_HOST}/${DEV_USERNAME}/kitchensink-conf ${BASE_DIR}/kitchensink-conf

printf "=> Setting up repos config"

git -C ${BASE_DIR}/kitchensink config --local user.email "${DEV_USERNAME}@ocp.com"
git -C ${BASE_DIR}/kitchensink config --local user.name "${DEV_USERNAME}"
git -C ${BASE_DIR}/kitchensink-conf config --local user.email "${DEV_USERNAME}@ocp.com"
git -C ${BASE_DIR}/kitchensink-conf config --local user.name "${DEV_USERNAME}"

printf "=> Uncomment driver line in install.sh\n"

if [ "$(uname)" == "Darwin" ]; then
  sed -i '' 's|# configure_drivers ${injected_dir}/driver-postgresql.env|configure_drivers ${injected_dir}/driver-postgresql.env|g' ${BASE_DIR}/kitchensink/extensions/install.sh
else
  sed -i 's|# configure_drivers ${injected_dir}/driver-postgresql.env|configure_drivers ${injected_dir}/driver-postgresql.env|g' ${BASE_DIR}/kitchensink/extensions/install.sh
fi

printf "=> Moving from 7.2 to 7.4\n"

yq e -i '.kitchensinkBuilderImage = "jboss-eap74-openjdk8-openshift:7.4.0"' ${BASE_DIR}/kitchensink-conf/cicd/values.yaml

printf "=> Commit and push kitchensink-conf\n"

git -C ${BASE_DIR}/kitchensink-conf commit -a -m "from poll_9.sh"
git -C ${BASE_DIR}/kitchensink-conf push origin main

ARGOCD_APP_NAME=openshift-gitops/kitchensink-cicd-${DEV_USERNAME}
# WAIT_FOR_HEALTH_FLAG="--health"

printf "=> ArgoCD refresh app: %s\n" "${ARGOCD_APP_NAME}"
argocd --grpc-web app get --refresh ${ARGOCD_APP_NAME} > /dev/null && \
argocd --grpc-web app wait ${ARGOCD_APP_NAME} --sync ${WAIT_FOR_HEALTH_FLAG}

printf "=> Commit and push kitchensink\n"

git -C ${BASE_DIR}/kitchensink commit -a -m "from poll_9.sh"
git -C ${BASE_DIR}/kitchensink push origin main

rm -rf  ${BASE_DIR}

