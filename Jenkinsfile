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
        IMAGE_TAG = "latest"
        HELM_CHART_NAME = "final-pj1"
        DOCKERHUB_CRED = credentials('docker_final_project')
        GIT_CREDENTIAL_ID = credentials('git_final_project')
        GIT_REPO = "noamra34/Noam1234"
        GIT_HUB_USR = "noamra34"
        
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
                    dockerImage = docker.build("${DOCKER_IMAGE_NAME}:1.0${BUILD_NUMBER}")
                    sh 'docker images'
                }
            }
        }

        // stage("Run Unit Tests") {
        //     steps {
        //         script {
        //             dockerImage.inside {
        //                 sh """
        //                     ls
        //                     PYTHONPATH=./flask_application pytest tests/ --junitxml=test-result.xml
        //                 """
        //             }
        //         }
        //     }
        //     post {
        //         always {
        //             junit 'test-result.xml'
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
                        dockerImage.push("1.0.${BUILD_NUMBER}")
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
        ///
    }
    ///
// sed -i 's/^  tag: .*/  tag: ${BUILD_NUMBER}/' ./final-pj1/values.yaml
//cat ./final-pj1/values.yaml
// git add ./final-pj1/values.yaml
    // post {
    //     when{
    //         expression {
    //                 return env.BRANCH_NAME == 'main'
    //             }
    //     }
    //     success {
    //         script {
    //             // Check if the latest commit message contains [ci skip]
    //             def skipCI = sh(returnStatus: true, script: "git log -1 --pretty=%B | grep -q '\\[ci skip\\]'") == 0
    //             if (!skipCI) {
    //                 // Trigger ArgoCD sync using CLI or API
    //                 sh "argocd app sync <your-application-name> --wait"
    //             } else {
    //                 echo "Skipping ArgoCD sync due to [ci skip] in commit message."
    //             }
    //         }
    //     }
    // }
    // post {
    //     success {
    //         script {
    //             def commitMessage = sh(script: "git log -1 --pretty=%B", returnStdout: true).trim()
    //             echo "Commit message: ${commitMessage}"
                
    //             // Check if the commit message contains [ci skip] (case insensitive)
    //             def skipCI = commitMessage =~ /(?i)\[ci skip\]/
                
    //             if (skipCI) {
    //                 currentBuild.result = 'SUCCESS'
    //                 error("Skipping build due to [ci skip] in commit message.")
    //             }
    //         }
    //     }
    // }

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

