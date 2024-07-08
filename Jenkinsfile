pipeline {
    agent {
        kubernetes {
            yamlFile 'build_pods.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }

    environment {
        DOCKER_IMAGE_NAME = "final_project"
        IMAGE_TAG = "latest"
        CHART_NAME = "final-pj1"
        CHART_YAML = "${CHART_NAME}/Chart.yaml"
        HELM_CHART_NAME = "final-pj1"
        DOCKERHUB_CRED = credentials('docker_final_project')
        GIT_CREDENTIAL_ID = credentials('git_final_project')
        GIT_REPO = "noamra34/Noam1234"
    }
    stages {
        stage("Checkout code") {
            steps {
                checkout scm
            }
        }

        stage("Build Docker Image") {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE_NAME}:${IMAGE_TAG}")
                    sh 'docker images'
                }
            }
        }

        // stage("Unit Test") {
        //     steps {
        //         script { 
        //             // sh "docker run -d -p 5000:5000 --name flaskapp ${DOCKER_IMAGE_NAME}"
        //             // sh 'docker exec flaskapp pytest <test_file>'
        //             sh 'pytest --junitxml=test-result.xml'
        //         }
        //         post {
        //             always {
        //                 junit 'test-result.xml'
        //             }
        //         }
        //     }
        // }


        

        stage("Create Merge request") {
            when {
                expression {
                    return env.BRANCH_NAME != 'main'
                }
            }
            steps{
                script {
                    def branchName = env.BRANCH_NAME
                    def mainBranch = "main"
                    def pullRequestTitle = "Merge ${branchName} into ${mainBranch}"
                    def pullRequestBody = "Automatically generated pull request to merge ${branchName} into ${mainBranch}"

                    sh """
                        curl -u ${GIT_CREDENTIAL_ID_USR}:${GIT_CREDENTIAL_ID_PSW} -X POST -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/${GIT_REPO}/pulls -d '{
                            "title": "${pullRequestTitle}",
                            "body": "${pullRequestBody}",
                            "head": "${branchName}",
                            "base": "${mainBranch}"
                        }'
                    """
                }
            }
        }
        stage("Push Artifacts") {
            when {
                expression {
                    return env.BRANCH_NAME == 'main'
                }
            }
            steps {
                script {
                    // Push Image To Docker Hub
                    docker.withRegistry('https://registry.hub.docker.com', 'docker_final_project') {
                        docker.image.push()
                    }

                    // Push Helm Chart To Docker Hub
                    sh "curl -u ${DOCKERHUB_CRED_USR}:${DOCKERHUB_CRED_PSW} -X PUT -H 'Content-Type: application/octet-stream' --data-binary @final-pj1-${IMAGE_TAG}.tgz https://registry.hub.docker.com/v1/repositories/noam476/tags/${IMAGE_TAG}"
                    
                }
            }
        }
        stage("Build Helm Package") {
            when {
                expression {
                    return env.BRANCH_NAME == 'main'
                }
            }
            steps {
                script {
                    
                    sh "sed -i.bak -e 's/^version: .*/version: ${BUILD_NUMBER}/' ${CHART_YAML}"
                    sh "helm upgrade ${HELM_CHART_NAME} ${CHART_NAME} --install --set image.tag=${IMAGE_TAG}"
                }
            }
        }

    }

    // post {
    //     failure {
    //         emailext subject: "Failed: ${currentBuild.fullDisplayName}",
    //                     body: "Build failed: ${env.BUILD_URL}",
    //                     to: "noamra34@gmail.com"
    //     }
    // }
}