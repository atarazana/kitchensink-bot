printf "=================\nEXECUTING STEP %s\n=================\n" "01"

GIT_SERVER="https://$(oc get route repository -n gitea-system -o jsonpath='{.spec.host}')"

cat <<EOF | oc apply -n openshift-gitops -f -
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: kitchensink-kustomize-${DEV_USERNAME}
  namespace: openshift-gitops
  labels:
    argocd-root-app: "true"
    username: ${DEV_USERNAME}
spec:
  generators:
  - list:
      elements:
      - env: dev
        ns: kustomize-dev-${DEV_USERNAME}
        desc: "Kustomize Dev"
      - env: test
        ns: kustomize-test-${DEV_USERNAME}
        desc: "Kustomize Test"
  template:
    metadata:
      name: kitchensink-kustomize-app-{{ env }}-${DEV_USERNAME}
      namespace: openshift-gitops
      labels:
        kitchensink-root-app: "true"
        username: ${DEV_USERNAME}
      finalizers:
      - resources-finalizer.argocd.argoproj.io
    spec:
      destination:
        namespace: '{{ ns }}'
        name: in-cluster
      ignoreDifferences:
      - group: apps.openshift.io
        kind: DeploymentConfig
        jqPathExpressions:
          - .spec.template.spec.containers[].image
      project: default
      syncPolicy:
        automated:
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
      source:
        path: kustomize/{{ env }}
        repoURL: "${GIT_SERVER}/${DEV_USERNAME}/kitchensink-conf"
        targetRevision: main
EOF