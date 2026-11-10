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
                echo 'Placeholder owned by B (Gabriel Renato): create the venv and install requirements.txt'
            }
        }

        stage('Test') {
            steps {
                echo 'Placeholder owned by B (Gabriel Renato): run pytest, publish JUnit and archive reports'
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
