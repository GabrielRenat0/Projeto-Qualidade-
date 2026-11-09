// Declarative pipeline for the NP2 delivery.
// Phase 0 skeleton: each stage and the post block only mark who owns that place.
// Each owner replaces only the echo in their own place.
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
                echo 'Placeholder owned by B (Gabriel Renato): run python -m build and archive dist/*'
            }
        }
    }

    post {
        always {
            echo 'Placeholder owned by D (Ian Romancini): send the e-mail with scripts/notify_email.py'
        }
    }
}
