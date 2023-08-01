printf "=================\nEXECUTING STEP %s\n=================\n" "01"

GIT_SERVER="https://$(oc get route repository -n gitea-system -o jsonpath='{.spec.host}')"

cat <<EOF | oc apply -n openshift-gitops -f -
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: kitchensink-cicd-${DEV_USERNAME}
  namespace: openshift-gitops
  labels:
    kitchensink-cicd-appset: "true"
spec:
  generators:
  - list:
      elements:
      - cluster: in-cluster
        ns: "cicd-tekton-${DEV_USERNAME}"
  template:
    metadata:
      name: kitchensink-cicd-${DEV_USERNAME}
      namespace: openshift-gitops
      labels:
        kitchensink-cicd-app: "true"
      finalizers:
      - resources-finalizer.argocd.argoproj.io
    spec:
      destination:
        namespace: '{{ ns }}'
        name: '{{ cluster }}'
      project: default
      syncPolicy:
        automated:
          selfHeal: true
      source:
        helm:
          parameters:
            - name: kitchensinkRepoUrl
              value: "${GIT_SERVER}/${DEV_USERNAME}/kitchensink"
            - name: kitchensinkRevision
              value: "main"
            - name: kitchensinkConfRepoUrl
              value: "${GIT_SERVER}/${DEV_USERNAME}/kitchensink-conf"
            - name: kitchensinkConfRevision
              value: "main"
            - name: username
              value: "${DEV_USERNAME}"
            - name: gitSslVerify
              value: "true"
            - name: cicdNamespace
              value: "cicd-tekton-${DEV_USERNAME}"
            - name: overlayDevNamespace
              value: "helm-kustomize-dev-${DEV_USERNAME}"
            - name: overlayTestNamespace
              value: "helm-kustomize-test-${DEV_USERNAME}"
            # - name: containerRegistryServer
            #   value: myregistry-quay-quay-system.apps.cluster-7mggs.7mggs.sandbox952.opentlc.com
            # - name: containerRegistryOrg
            #   value: ${DEV_USERNAME}
        path: cicd
        repoURL: "${GIT_SERVER}/${DEV_USERNAME}/kitchensink-conf"
        targetRevision: main
EOF

printf "=================\nEXECUTING STEP %s\n=================\n" "02"

GIT_PAT=$(curl -k -s -XPOST -H "Content-Type: application/json" \
  -d '{"name":"cicd'"${RANDOM}"'","scopes": ["repo"]}' \
  -u ${DEV_USERNAME}:openshift \
  ${GIT_SERVER}/api/v1/users/${DEV_USERNAME}/tokens | jq -r .sha1)
echo "GIT_PAT=${GIT_PAT}"

printf "=================\nEXECUTING STEP %s\n=================\n" "03"

cat <<EOF | oc apply -n cicd-tekton-${DEV_USERNAME} -f -
apiVersion: v1
kind: Secret
metadata:
  name: git-pat-secret
  namespace: cicd-tekton-${DEV_USERNAME}
type: kubernetes.io/basic-auth
stringData:
  user.name: ${DEV_USERNAME}
  user.email: "${DEV_USERNAME}@example.com"
  username: ${DEV_USERNAME}
  password: ${GIT_PAT}
EOF

oc annotate -n cicd-tekton-${DEV_USERNAME} secret git-pat-secret \
  "tekton.dev/git-0=${GIT_SERVER}"

printf "=================\nEXECUTING STEP %s\n=================\n" "04"

KITCHENSINK_CI_EL_LISTENER_HOST=$(oc get route/el-kitchensink-ci-pl-push-gitea-listener -n cicd-tekton-${DEV_USERNAME} -o jsonpath='{.status.ingress[0].host}')

curl -k -X 'POST' "${GIT_SERVER}/api/v1/repos/${DEV_USERNAME}/kitchensink/hooks" \
  -H "accept: application/json" \
  -H "Authorization: token ${GIT_PAT}" \
  -H "Content-Type: application/json" \
  -d '{
  "active": true,
  "branch_filter": "*",
  "config": {
     "content_type": "json",
     "url": "http://'"${KITCHENSINK_CI_EL_LISTENER_HOST}"'"
  },
  "events": [
    "push"
  ],
  "type": "gitea"
}'

KITCHENSINK_CD_EL_LISTENER_HOST=$(oc get route/el-kitchensink-cd-pl-pr-gitea-listener -n cicd-tekton-${DEV_USERNAME} -o jsonpath='{.status.ingress[0].host}')

curl -k -X 'POST' "${GIT_SERVER}/api/v1/repos/${DEV_USERNAME}/kitchensink-conf/hooks" \
  -H "accept: application/json" \
  -H "Authorization: token ${GIT_PAT}" \
  -H "Content-Type: application/json" \
  -d '{
  "active": true,
  "branch_filter": "*",
  "config": {
     "content_type": "json",
     "url": "http://'"${KITCHENSINK_CD_EL_LISTENER_HOST}"'"
  },
  "events": [
    "pull_request"
  ],
  "type": "gitea"
}'