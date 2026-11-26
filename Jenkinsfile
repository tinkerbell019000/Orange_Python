pipeline {
    agent any

    parameters {
        choice(name: 'SUITE', choices: ['all', 'smoke', 'regression'], description: 'Select pytest marker suite to run')
        choice(name: 'BROWSER', choices: ['chrome', 'firefox', 'webkit'], description: 'Browser to execute tests on')
        string(name: 'WORKERS', defaultValue: '1', description: 'Number of parallel pytest-xdist workers (use 1 for shared session)')
    }

    environment {
        IMAGE_NAME     = "orangehrm-playwright-tests"
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = "orangehrm-runner-${env.BUILD_NUMBER}"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timeout(time: 120, unit: 'MINUTES')
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
                    sh """
                        docker build \
                          --cache-from ${IMAGE_NAME}:latest \
                          -t ${IMAGE_NAME}:latest \
                          -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    """
                }
            }
        }

        stage('Run Playwright Automation Tests') {
            steps {
                script {
                    def markerFlag = params.SUITE == 'all' ? '' : "-m ${params.SUITE}"
                    def workerFlag = params.WORKERS.toInteger() > 1 ? "-n ${params.WORKERS}" : ''

                    sh "rm -rf reports && mkdir -p reports/screenshots"

                    try {
                        sh """
                            docker run --name ${CONTAINER_NAME} --ipc=host \
                              -e HEADLESS=true \
                              -e BROWSER=${params.BROWSER} \
                              ${IMAGE_NAME}:${IMAGE_TAG} \
                              pytest -v ${markerFlag} ${workerFlag}
                        """
                    } finally {
                        sh "docker cp ${CONTAINER_NAME}:/app/reports/. ./reports/ || true"
                        sh "docker rm -f ${CONTAINER_NAME} || true"
                    }
                }
            }
        }
    }

    post {
        always {
            publishHTML(target: [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'test_results.html',
                reportName: 'Playwright Pytest Report'
            ])

            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true

            // Keep :latest cached so pip & playwright layers are reused on future builds
            sh "docker rmi -f ${IMAGE_NAME}:${IMAGE_TAG} || true"
        }
        success {
            echo "Automation Suite PASSED on ${params.BROWSER} (${params.SUITE})!"
        }
        failure {
            echo "Automation Suite FAILED. Check 'Playwright Pytest Report' and archived screenshots."
        }
    }
}
