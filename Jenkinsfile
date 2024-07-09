pipeline {
    agent {
        kubernetes {
            yamlFile 'build_pods.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }

    environment {
        DOCKER_IMAGE_NAME = "noam476/final-project"
        IMAGE_TAG = "latest"
        HELM_CHART_NAME = "final-pj1"
        DOCKERHUB_CRED = credentials('docker_final_project')
        GIT_CREDENTIAL_ID = credentials('git_final_project')
        GIT_REPO = "noamra34/Noam1234"
        GIT_HUB_USR = "noamra34"
        //hello
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

        
        // 

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
                        dockerImage.push("latest")
                    }
                }
            }
        }
        // stage("Build Helm Package") {
        //     when {
        //         expression {
        //             return env.BRANCH_NAME == 'main'
        //         }
        //     }
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
                        sed -i 's/^version: .*/version: ${BUILD_NUMBER}/' ./final-pj1/Chart.yaml
                        cat ./final-pj1/Chart.yaml
                        git config --global --add safe.directory ${WORKSPACE}
                        git config user.name "${GIT_HUB_USR}"
                        git config user.email "noamra34@gmail.com"
                        git add ./final-pj1/Chart.yaml
                        git commit -m "Update Chart version [ci skip]"
                        echo ${BRANCH_NAME}
                        git fetch origin
                        git checkout main
                        git push origin main
                        """
                }
            }
        }
    }
    post {
        success {
            script {
                // Check if the latest commit message contains [ci skip]
                def skipCI = sh(returnStatus: true, script: "git log -1 --pretty=%B | grep -q '\\[ci skip\\]'") == 0
                if (skipCI) {
                    // If [ci skip] is found, set the build result to SUCCESS and stop further execution
                    currentBuild.result = 'SUCCESS'
                    error("Skipping build due to [ci skip] in commit message.")
                }
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
        // stage("Update Chart.yaml in Main Branch") {
        //     when {
        //         expression {
        //             return env.BRANCH_NAME == 'main'
        //         }
        //     }
        //     when {
        //         beforeAgent true
        //         expression {
        //             // Check if there's a tag indicating we should proceed
        //             return sh(script: "git tag --list 'update-chart-*'", returnStatus: true) == 0
        //         }
        //     }
        // }        

