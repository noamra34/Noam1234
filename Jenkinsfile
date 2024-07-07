pipeline{
    agent {
        kubernetes {
            yamlFile = 'build_pods.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }

    environment{
        DOCKER_IMAGE_NAME = "final_project"
        IMAGE_TAG = "latest"

    }
    stages{
        stage("Checkout code"){
            steps{
                checkout scm
            }
        }

        stage("Build Docker Image"){
            steps{
                script{
                    docker.build("${DOCKER_IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }

        stage("Unit Test"){
            steps{
                script{
                    sh 'pytest --junitxml=test-result.xml'
                }
                post{
                    always{
                        junit 'test-result.xml'
                    }
                }
            }
        }

        stage("Build Helm Package"){
            steps{
                script{
                    sh 'helm package ./final-pj1'
                }
            }
        }
    }
    
    post{
        failure{
            emailext subject: "Failed: ${currentBuild.fullDisplayName}",
                        body: "Build failed: ${env.BUILD_URL}",
                        to: "noamra34@gmail.com"
        }
    }
}