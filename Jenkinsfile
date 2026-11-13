// Declarative pipeline for the NP2 delivery.
// Setup, Test and Build: B (Gabriel Renato). post { always }: D (Ian Romancini).
// Each owner edits only their own place.
pipeline {
    agent any

    options {
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    stages {
        stage('Setup') {
            steps {
                // Start clean, so a build never publishes reports or packages left by an older one.
                sh 'rm -rf reports dist build *.egg-info'
                sh 'python3 -m venv --clear .venv'
                sh '.venv/bin/pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                // Same command as on a laptop and in the tests container; the rest comes from pytest.ini.
                sh '.venv/bin/pytest --junitxml=reports/junit.xml'
            }
            post {
                // Runs even when a test fails, so the results and reports are always kept.
                always {
                    junit testResults: 'reports/junit.xml', allowEmptyResults: true
                    archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
                }
            }
        }

        stage('Build') {
            steps {
                sh '.venv/bin/python -m build'
                // The fingerprint records the MD5 of each package, so Jenkins can trace it later.
                archiveArtifacts artifacts: 'dist/*', fingerprint: true
            }
        }
    }

    post {
        // Runs on success and on failure, so the e-mail also reports a broken build.
        always {
            // The result and the duration are not environment variables, so they are passed here.
            // While post runs, the duration still ends with " and counting".
            withEnv([
                "BUILD_STATUS=${currentBuild.currentResult}",
                "BUILD_DURATION=${currentBuild.durationString.replace(' and counting', '')}",
            ]) {
                // The system python3, not the venv: the e-mail must go out even if Setup failed.
                sh 'python3 scripts/notify_email.py --status "$BUILD_STATUS"'
            }
        }
    }
}
