oc apply -f - <<EOF
---
kind: Secret
apiVersion: v1
metadata:
  name: slack-webhook-secret
stringData:
  slack-webhook-url: ${SLACK_WEBHOOK}
type: Opaque
---
apiVersion: monitoring.coreos.com/v1beta1
kind: AlertmanagerConfig
metadata:
  name: fruit-gateway-routing
  namespace: ${PROJECT_NAME}
spec:
  receivers:
    - name: slack
      slackConfigs:
        - apiURL:
            key: slack-webhook-url
            name: slack-webhook-secret
          channel: '#${SLACK_CHANNEL}'
          DEV_USERNAME: 'AlertManager'
          title: 'Kitchensink Alert "{{ .CommonLabels.alertname }}" 🚀'
          text: |
            {{ .CommonAnnotations.summary }}

            {{ range .Alerts }}
              *Alert:* {{ .Labels.alertname }}
              *Description:* {{ .Annotations.description }}
              *Status:* {{ .Status | toUpper }}
              *Severity:* {{ .Labels.severity }}
              *SpecialType:* {{ .Labels.special_type }}
              *Time:* {{ .StartsAt }}
              *Alerts*: https://console-openshift-console.apps.${CLUSTER_DOMAIN}/dev-monitoring/ns/${PROJECT_NAME}/alerts
              *Logs*: https://kibana-openshift-logging.apps.${CLUSTER_DOMAIN}/app/kibana#/discover?_g=(time:(from:now-1w,mode:relative,to:now))&_a=(columns:!(kubernetes.container_name,message),interval:auto,query:(language:lucene,query:'kubernetes.namespace_name:%22${PROJECT_NAME}%22%20AND%20kubernetes.container_name.raw:%22fruit-gateway%22%20AND%20message:"ERROR"'),sort:!('@timestamp',desc))
              *Traces*: https://jaeger-all-in-one-inmemory-kitchensink-infra.apps.${CLUSTER_DOMAIN}/search?limit=20&lookback=1h&maxDuration&minDuration&service=fruit-gateway
            {{ end }}
  route:
    receiver: slack
    repeatInterval: "1m"
    routes:
      - receiver: slack
EOF