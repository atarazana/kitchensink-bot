FROM registry.access.redhat.com/ubi8/python-311:1-13

ENV ARGOCD_VERSION=v2.7.7
ENV OC_VERSION=4.12.22

USER root

RUN curl -o /tmp/argocd -L https://github.com/argoproj/argo-cd/releases/download/${ARGOCD_VERSION}/argocd-linux-amd64 && cd /usr/bin && cp /tmp/argocd . && chmod a+x /usr/bin/argocd && rm -f /tmp/argocd
RUN curl -o /tmp/oc.tar.gz -L https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/${OC_VERSION}/openshift-client-linux-${OC_VERSION}.tar.gz && cd /usr/bin && tar -xvzf /tmp/oc.tar.gz && chmod a+x /usr/bin/oc && chmod a+x /usr/bin/kubectl && rm -f /tmp/oc.tar.gz

USER 1001

# Create directory for application resources
COPY --chown=1001 *.py /deployments/
COPY --chown=1001 requirements.txt /deployments/
COPY --chown=1001 data/ /deployments/data/
COPY --chown=1001 listeners/ /deployments/listeners/

WORKDIR /deployments

# Install dependencies
RUN pip install -r requirements.txt

# Configure container port and UID
EXPOSE 8080
USER 1001

# Run application
CMD ["python", "/deployments/app.py"] 