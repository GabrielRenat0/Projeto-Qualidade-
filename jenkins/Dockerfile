# Pinned LTS tag: upgrade on purpose, never with a floating tag.
FROM jenkins/jenkins:2.580.2-lts-jdk21

# Python runs the pipeline stages (venv, pytest, build) and the notification script.
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*
USER jenkins

# Everything is configured as code, so the setup wizard is skipped.
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# JCasC reads every YAML file in this folder. It lives outside /var/jenkins_home on purpose:
# that path is a volume, and a volume would keep an old copy after an image upgrade.
ENV CASC_JENKINS_CONFIG=/usr/share/jenkins/casc
COPY --chown=jenkins:jenkins casc/ /usr/share/jenkins/casc/
