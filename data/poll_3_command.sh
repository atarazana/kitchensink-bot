printf "=================\nEXECUTING STEP %s\n=================\n" "01"

cat <<EOF | oc apply -n openshift-gitops -f -
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: kitchensink-basic-${DEV_USERNAME}
  namespace: openshift-gitops
  labels:
    argocd-root-app: "true"
    username: ${DEV_USERNAME}
spec:
  generators:
  - list:
      elements:
      - env: appset-a-${DEV_USERNAME}
        desc: "ApplicationSet A"
      - env: appset-b-${DEV_USERNAME}
        desc: "ApplicationSet B"
  template:
    metadata:
      name: kitchensink-basic-app-{{ env }}
      namespace: openshift-gitops
      labels:
        kitchensink-root-app: "true"
        username: ${DEV_USERNAME}
      finalizers:
      - resources-finalizer.argocd.argoproj.io
    spec:
      destination:
        namespace: '{{ env }}'
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
        path: basic/base
        repoURL: "${GIT_SERVER}/${DEV_USERNAME}/kitchensink-conf"
        targetRevision: main
EOF