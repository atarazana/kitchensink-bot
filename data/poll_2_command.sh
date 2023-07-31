printf "=================\nEXECUTING STEP %s\n=================\n" "01"

cat <<EOF | oc apply -n openshift-gitops -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: kitchensink-basic-app-${DEV_USERNAME}
  namespace: openshift-gitops
  finalizers:
    - resources-finalizer.argocd.argoproj.io
  labels:
    kitchensink-root-app: 'true'
    username: ${DEV_USERNAME}
spec:
  destination:
    name: in-cluster
    namespace: argo-${DEV_USERNAME}
  ignoreDifferences:
    - group: apps.openshift.io
      jqPathExpressions:
        - '.spec.template.spec.containers[].image'
      kind: DeploymentConfig
  project: default
  source:
    path: basic/base
    repoURL: "${GIT_SERVER}/${DEV_USERNAME}/kitchensink-conf"
    targetRevision: main
  syncPolicy:
    automated:
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
EOF