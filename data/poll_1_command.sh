printf "=================\nEXECUTING STEP %s\n=================\n" "01"

GIT_SERVER="https://$(oc get route repository -n gitea-system -o jsonpath='{.spec.host}')"

oc new-project s2i-${DEV_USERNAME}

oc adm policy add-role-to-user edit ${DEV_USERNAME} -n s2i-${DEV_USERNAME}
oc adm policy add-role-to-user monitoring-edit ${DEV_USERNAME} -n s2i-${DEV_USERNAME}
oc adm policy add-role-to-user alert-routing-edit ${DEV_USERNAME} -n s2i-${DEV_USERNAME}

oc new-app --name=kitchensink-db \
 -e POSTGRESQL_USER=luke \
 -e POSTGRESQL_PASSWORD=secret \
 -e POSTGRESQL_DATABASE=kitchensink centos/postgresql-10-centos7 \
 --as-deployment-config=false

oc label deployment/kitchensink-db app.kubernetes.io/part-of=kitchensink-app --overwrite=true && \
oc label deployment/kitchensink-db app.openshift.io/runtime=postgresql --overwrite=true

printf "=================\nEXECUTING STEP %s\n=================\n" "02"

oc patch deployment kitchensink-db --type json -p '
[{
  "op": "add",
  "path": "/spec/template/spec/securityContext",
  "value": {
    "runAsNonRoot": true,
    "seccompProfile": {
      "type": "RuntimeDefault"
    }
  }
},
{
  "op": "add",
  "path": "/spec/template/spec/containers/0/securityContext",
  "value": {
    "allowPrivilegeEscalation": false,
    "capabilities": {
      "drop": ["ALL"]
    }
  }
}]'

printf "=================\nEXECUTING STEP %s\n=================\n" "03"

oc new-app --template=eap72-basic-s2i \
-p APPLICATION_NAME=kitchensink \
-p MAVEN_ARGS_APPEND="-Dcom.redhat.xpaas.repo.jbossorg" \
-p SOURCE_REPOSITORY_URL="${GIT_SERVER}/${DEV_USERNAME}/kitchensink" \
-p SOURCE_REPOSITORY_REF=main \
-p CONTEXT_DIR=. && \
oc rollout pause dc/kitchensink

printf "=================\nEXECUTING STEP %s\n=================\n" "04"

oc set env dc/kitchensink DB_HOST=kitchensink-db DB_PORT=5432 DB_NAME=kitchensink DB_USERNAME=luke DB_PASSWORD=secret && \
oc set probe dc/kitchensink --readiness --initial-delay-seconds=40 --failure-threshold=15 --period-seconds=5 && \
oc set probe dc/kitchensink --liveness  --initial-delay-seconds=40 --failure-threshold=15 --period-seconds=5 && \
oc rollout resume dc/kitchensink

oc label dc/kitchensink app.kubernetes.io/part-of=kitchensink-app --overwrite=true && \
oc label dc/kitchensink app.openshift.io/runtime=jboss --overwrite=true

oc annotate dc/kitchensink \
 app.openshift.io/connects-to='[{"apiVersion":"apps/v1","kind":"Deployment","name":"kitchensink-db"}]' \
 --overwrite=true