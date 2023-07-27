oc apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: fruit-gateway-alert-rules
  namespace: ${PROJECT_NAME}
  labels:
    openshift.io/prometheus-rule-evaluation-scope: leaf-prometheus
spec:
  groups:
  - name: fruit-gateway-monitoring
    rules:
    - alert: too-many-accumulated-errors
      annotations:
        description: 'Accumulated errors'
        summary: |
          This alert is triggered if there are too many accumulated errors in a predefined period of time.
      expr: acc_errors_count_total > 4
      for: 1m
      labels:
        severity: warning
        special_type: kitchensink
        alert_type: custom
EOF