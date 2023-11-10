printf "=================\nEXECUTING STEP %s\n=================\n" "01"

GIT_SERVER="https://$(oc get route repository -n gitea-system -o jsonpath='{.spec.host}')"

cat <<EOF | oc apply -n openshift-gitops -f -
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: kitchensink-kustomized-helm-${DEV_USERNAME}
  namespace: openshift-gitops
  labels:
    argocd-root-app: "true"
    username: ${DEV_USERNAME}
spec:
  generators:
  - list:
      elements:
      - env: dev
        ns: helm-kustomize-dev-${DEV_USERNAME}
        desc: "Helm + Kustomize (Dev)"
      - env: test
        ns: helm-kustomize-test-${DEV_USERNAME}
        desc: "Helm + Kustomize (Test)"
  template:
    metadata:
      name: kitchensink-kustomized-helm-app-{{ env }}-${DEV_USERNAME}
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
      project: default
      syncPolicy:
        automated:
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
      source:
        path: advanced/overlays/{{ env }}
        repoURL: "${GIT_SERVER}/${DEV_USERNAME}/kitchensink-conf"
        targetRevision: main
        plugin:
          env:
            - name: DEBUG
              value: 'false'
            - name: BASE_NAMESPACE
              value: 'cicd-tekton-${DEV_USERNAME}'
          # This overrides the discover spec in ConfigManagementPlugin
          # https://github.com/atarazana/kitchensink/blob/main/util/bootstrap/3.adapt-operators/gitops-patch.yaml#L80
          name: kustomized-helm-v1.0
EOF
