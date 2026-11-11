# Same Python minor version as the Jenkins image, pinned.
FROM python:3.13.18-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN groupadd --gid 1000 tester \
    && useradd --uid 1000 --gid 1000 --create-home tester

WORKDIR /app

# Dependencies first, so code-only changes reuse this cached layer.
COPY requirements.txt .
RUN pip install -r requirements.txt

# The whole repository: the configuration tests also read docker-compose.yml,
# the Jenkinsfile and the jenkins/ folder.
COPY --chown=tester:tester . .

# Both owned by tester: pytest and coverage write their cache and data files in /app,
# and the named volume mounted on reports inherits a writable directory.
RUN mkdir -p reports && chown tester:tester /app reports

USER tester

# Same command the Jenkins Test stage runs.
CMD ["pytest", "--junitxml=reports/junit.xml"]
