printf "=================\nEXECUTING STEP %s\n=================\n" "01"

GIT_SERVER="https://$(oc get route repository -n gitea-system -o jsonpath='{.spec.host}')"

cat <<EOF | oc apply -n openshift-gitops -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: kitchensink-helm-app-${DEV_USERNAME}
  namespace: openshift-gitops
  finalizers:
    - resources-finalizer.argocd.argoproj.io
  labels:
    kitchensink-root-app: 'true'
    username: ${DEV_USERNAME}
spec:
  destination:
    name: in-cluster
    namespace: helm-${DEV_USERNAME}
  ignoreDifferences:
    - group: apps
      jqPathExpressions:
        - '.spec.template.spec.containers[].image'
      kind: Deployment
  project: default
  source:
    helm:
      parameters:
        - name: debug
          value: 'true'
        - name: baseNamespace
          value: 'helm-${DEV_USERNAME}'
    path: advanced/helm_base
    repoURL: "${GIT_SERVER}/${DEV_USERNAME}/kitchensink-conf"
    targetRevision: main
  syncPolicy:
    automated:
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
EOF