pipeline {
    agent any

    parameters {
        choice(name: 'SUITE', choices: ['smoke', 'regression', 'all'], description: 'Select pytest marker suite to run')
        choice(name: 'BROWSER', choices: ['chrome', 'firefox', 'webkit'], description: 'Browser to execute tests on')
        string(name: 'WORKERS', defaultValue: '1', description: 'Number of parallel pytest-xdist workers (use 1 for shared session)')
    }

    environment {
        IMAGE_NAME = "orangehrm-playwright-tests"
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Test Docker Image') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        stage('Run Playwright Automation Tests') {
            steps {
                script {
                    def markerFlag = params.SUITE == 'all' ? '' : "-m ${params.SUITE}"
                    def workerFlag = params.WORKERS.toInteger() > 1 ? "-n ${params.WORKERS}" : ''

                    // Ensure clean reports directory on Jenkins workspace before run
                    sh "rm -rf reports && mkdir -p reports/screenshots"

                    // Mount workspace/reports into container so HTML report & screenshots survive container exit
                    sh """
                        docker run --rm --ipc=host \
                          -e HEADLESS=true \
                          -e BROWSER=${params.BROWSER} \
                          -v "\$(pwd)/reports:/app/reports" \
                          ${IMAGE_NAME}:${IMAGE_TAG} \
                          pytest -v ${markerFlag} ${workerFlag} \
                          --html=reports/test_results.html --self-contained-html
                    """
                }
            }
        }
    }

    post {
        always {
            // Publish HTML Report even when tests fail
            publishHTML(target: [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'test_results.html',
                reportName: 'Playwright Pytest Report'
            ])

            // Archive screenshots & HTML report as build artifacts
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true

            // Clean up built image to prevent disk space exhaustion
            sh "docker rmi -f ${IMAGE_NAME}:${IMAGE_TAG} || true"
            sh "docker image prune -f || true"
        }
        success {
            echo "Automation Suite PASSED on ${params.BROWSER} (${params.SUITE})!"
        }
        failure {
            echo "Automation Suite FAILED. Check 'Playwright Pytest Report' and archived screenshots."
        }
    }
}
