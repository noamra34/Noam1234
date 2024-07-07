pipeline{
    agent {
        kubernetes {
            yamlFile 'build_pods.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }

    environment{
        DOCKER_IMAGE_NAME = "final_project"
        IMAGE_TAG = "latest"
        HELM_CHART_NAME = "final-pj1"
        DOCKERHUB_CRED = credentials('docker_final_project')
        GIT_CREDENTIAL_ID = credentials('git_final_project')
        GIT_REPO = "noamra34/Noam1234"
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
                    sh 'helm package ./${HELM_CHART_NAME} --version ${IMAGE_TAG}'
                }
            }
        }

        stage("Psh Artifacts"){
            when{
                expression {
                    return env.BRANCH_NAME == 'main'
                }
            }
            steps{
                script{
                    // Push Image To Docker Hub
                    docker.withregistry('https://registry.hub.docker.com', 'docker_final_project'){
                        docker.image("${DOCKER_IMAGE_NAME}:${IMAGE_TAG}").push()
                    }

                    // Push Helm Chart To Docker Hub
                    sh "curl -u $DOCKERHUB_CRED_USR:$DOCKERHUB_CRED_PSW -X PUT -H 'Content-Type: application/octet-stream' --data-binary @final-pj1-${IMAGE_TAG}.tgz https://registry.hub.docker.com/v1/repositories/noam476/tags/${IMAGE_TAG}"
                }
            }
        }

        stage("Create Merge request"){
            when{
                exspression {
                    return env.BRANCH_NAME != 'main'
                }
            }
            steps{
                script{
                    def branchName = env.BRANCH_NAME
                    def mainBranch = "main"
                    def pullRequestTitle = "Merge ${branchName} into ${mainBranch}"
                    def pullRequestBody = "Automatically generated pull request to merge ${branchName} into ${mainBranch}"

                    sh """
                        curl -u GIT_CREDENTIAL_ID_USR:GIT_CREDENTIAL_ID_PSW -X POST -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/${GIT_REPO}/pulls -d '{
                            "title": "${pullRequestTitle}"
                            "body": "${pullRequestBody}"
                            "head": "${branchName}"
                            "base": "${mainBranch}"
                        }'
                    """
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