FROM registry.access.redhat.com/ubi8/python-311:1-13

ENV ARGOCD_VERSION=v2.7.7
ENV OC_VERSION=4.12.22
ENV YQ_VERSION=4.11.2
ENV HELM_VERSION=3.11.2

USER root

RUN dnf install -y tar gzip openssh-clients jq rsync && dnf module reset -y nodejs && dnf module install -y nodejs:16/common

RUN curl -o /tmp/argocd -L https://github.com/argoproj/argo-cd/releases/download/${ARGOCD_VERSION}/argocd-linux-amd64 && cd /usr/bin && cp /tmp/argocd . && chmod a+x /usr/bin/argocd && rm -f /tmp/argocd
RUN curl -o /tmp/oc.tar.gz -L https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/${OC_VERSION}/openshift-client-linux-${OC_VERSION}.tar.gz && cd /usr/bin && tar -xvzf /tmp/oc.tar.gz && chmod a+x /usr/bin/oc && chmod a+x /usr/bin/kubectl && rm -f /tmp/oc.tar.gz
RUN curl -s -o /tmp/yq -L https://github.com/mikefarah/yq/releases/download/v${YQ_VERSION}/yq_linux_amd64 && cd /usr/bin && cp /tmp/yq . && chmod a+x /usr/bin/yq && rm -f /tmp/yq
RUN curl -s -o /tmp/helm.tar.gz -L https://get.helm.sh/helm-v${HELM_VERSION}-linux-amd64.tar.gz && cd /usr/bin && tar -xvzf /tmp/helm.tar.gz linux-amd64/helm && mv /usr/bin/linux-amd64/helm /usr/bin/helm && rm -rf /usr/bin/linux-amd64 && chmod a+x /usr/bin/helm && rm -f /tmp/helm.tar.gz

RUN dnf -y clean all --enablerepo='*'

RUN mkdir ${HOME}/.config && chgrp -R 0 ${HOME} && chmod -R g=u ${HOME}

USER 1001

# NodeJS
# ENV NVM_DIR="${HOME}/.nvm"
# ENV NODEJS_VERSION=16.14.0
# RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
# RUN source ${NVM_DIR}/nvm.sh && nvm install v${NODEJS_VERSION} && nvm alias default v$NODEJS_VERSION && nvm use v$NODEJS_VERSION && npm install --global yarn@v1.22.17
# ENV PATH=$NVM_DIR/versions/node/v$NODEJS_VERSION/bin:$PATH
# ENV NODEJS_HOME_16=$NVM_DIR/versions/node/v$NODEJS_VERSION

# Create directory for application resources
COPY --chown=1001 *.py /deployments/
COPY --chown=1001 requirements.txt /deployments/
COPY --chown=1001 data/ /deployments/data/
COPY --chown=1001 listeners/ /deployments/listeners/
COPY --chown=1001 rest/ /deployments/rest/
COPY --chown=1001 poll-ui/ /deployments/poll-ui/

RUN chmod a+x /deployments/data/*.sh

RUN npm --prefix /deployments/poll-ui/ install && npm --prefix /deployments/poll-ui/ run build

WORKDIR /deployments

# Install dependencies
RUN pip install -r requirements.txt

# Configure container port and UID
EXPOSE 5000
USER 1001

# Run application
CMD ["python", "/deployments/app.py"] 