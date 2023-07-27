oc apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    k8s-app: prometheus
  name: fruit-gateway-monitor
  namespace: ${PROJECT_NAME}
spec:
  endpoints:
    - interval: 30s
      path: /q/metrics
      port: http
  namespaceSelector:
    matchNames:
    - ${PROJECT_NAME}
  selector:
    matchLabels:
      app.kubernetes.io/name: fruit-gateway
EOF