pipeline {
    agent {
        kubernetes {
            yamlFile 'build_pods.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }
//hello
    environment {
        DOCKER_IMAGE_NAME = "noam476/final-project"
        IMAGE_TAG = "1.0.${BUILD_NUMBER}"
        HELM_CHART_NAME = "final-pj1"
        DOCKERHUB_CRED = credentials('docker_final_project')
        GIT_CREDENTIAL_ID = credentials('git_final_project')
        GIT_REPO = "noamra34/Noam1234"
        GIT_HUB_USR = "noamra34"
        DOCKER_COMPOSE_VERSION = "1.29.2"
        
    }
    stages {
        stage('Run CI?') {
            when {
                expression {
                    return env.BRANCH_NAME == 'main'
                }
            }
            steps {
                script {
                    sh "git config --global --add safe.directory /home/jenkins/agent/workspace/final_project_main"
                    def ciskip = (sh(script: "git log -1 --pretty=%B | fgrep -ie '[skip ci]' -e '[ci skip]'", returnStatus: true) == 0)
                    if (ciskip) {
                        echo "Commit message contains [ci skip] or [skip ci]. Updating ArgoCD and stopping pipeline."
                        currentBuild.result = 'NOT_BUILT'
                        error 'Aborting because commit message contains [skip ci]'
                    }
                    else {
                        echo "No [ci skip] or [skip ci] found. Proceeding with pipeline."
                    }
                    
                }
            }
        }
        stage("Checkout code") {
            steps {
                checkout scm
            }
        }

        stage("Build Docker Image") {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE_NAME}:1.0.${BUILD_NUMBER}")
                    sh 'docker images'
                }
            }
        }
//         stage('Start Containers with Docker Compose') {
//             steps {
//                 script {
//                     // Install Docker Compose if necessary
                    
//                     // Bring up containers using Docker Compose
//                     sh """
//                         docker-compose -f docker-compose.yaml up -d
//                         docker-compose exec app pytest -v

//                     """
//                 }
//             }
//         }
// //
//         stage('Cleanup') {
//             steps {
//                 script {
//                     // Clean up: stop and remove containers
//                     sh "docker-compose -f docker-compose.yaml down"
//                 }
//             }
//         }
    

        // stage("Run Unit Tests") {
        //     steps {
        //         script {
        //             dockerImage.inside {
        //                 sh """
        //                     ls
        //                     pytest -q
        //                 """
        //             }
        //         }
        //     }


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
                        dockerImage.push("1.0.${BUILD_NUMBER}")
                    }
                }
            }
        }
     stage("Build Helm Package") {
        //     when {
        //         expression {
        //             return env.BRANCH_NAME == 'main'
        //         }
        //     }
        //
        stage("Update Chart.yaml in Main Branch") {
            when {
                expression {
                    return env.BRANCH_NAME == 'main'
                }
            }
            steps {
                script {
                    sh """
                        cd ${WORKSPACE}
                        echo "Current working directory: \$(pwd)"
                        ls -la
                        sed -i 's/^version: .*/version: 1.0.${BUILD_NUMBER}/' ./final-pj1/Chart.yaml
                        sed -i 's/^  tag: .*/  tag: 1.0.${BUILD_NUMBER}/' ./final-pj1/values.yaml
                        cat ./final-pj1/Chart.yaml
                        cat ./final-pj1/values.yaml
                        git config --global --add safe.directory ${WORKSPACE}
                        git config user.name "${GIT_HUB_USR}"
                        git config user.email "noamra34@gmail.com"
                        git add ./final-pj1/Chart.yaml
                        git add ./final-pj1/values.yaml
                        git commit -m "Update ${BUILD_NUMBER} Chart version [ci skip]"
                        echo ${BRANCH_NAME}
                        git push "https://${GIT_CREDENTIAL_ID_USR}:${GIT_CREDENTIAL_ID_PSW}@github.com/${GIT_REPO}.git" HEAD:main
                        """
                }
            }
        }
        
    }
    post {
        failure {
            cleanWs()
        }
    }
}