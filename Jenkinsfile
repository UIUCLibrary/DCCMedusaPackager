#!groovy
@Library("ds-utils")
import org.ds.*

pipeline {
    agent {
        label "Windows"
    }
    environment {
        mypy_args = "--junit-xml=mypy.xml"
        pytest_args = "--junitxml=reports/junit-{env:OS:UNKNOWN_OS}-{envname}.xml --junit-prefix={env:OS:UNKNOWN_OS}  --basetemp={envtmpdir}"
    }
    parameters {
        string(name: "PROJECT_NAME", defaultValue: "Medusa Packager", description: "Name given to the project")
        booleanParam(name: "UNIT_TESTS", defaultValue: true, description: "Run Automated Unit Tests")
        booleanParam(name: "ADDITIONAL_TESTS", defaultValue: true, description: "Run additional tests")
        booleanParam(name: "UPDATE_DOCS", defaultValue: false, description: "Update the documentation")
        string(name: 'URL_SUBFOLDER', defaultValue: "DCCMedusaPackager", description: 'The directory that the docs should be saved under')
        booleanParam(name: "PACKAGE", defaultValue: true, description: "Create a Packages")
        booleanParam(name: "DEPLOY", defaultValue: false, description: "Deploy SCCM")
    }

    stages {
        stage("Cloning Source") {
            agent any

            steps {
                deleteDir()
                echo "Cloning source"
                checkout scm
                stash includes: '**', name: "Source"
                stash includes: 'deployment.yml', name: "Deployment"

            }
        }
        stage("Unit tests") {
            when {
                expression { params.UNIT_TESTS == true }
            }
            steps {
                parallel(
                    "Windows": {
                        node(label: "Windows") {
                            script {
                                checkout scm
                                try {
                                    bat "${tool 'Python3.6.3_Win64'} -m tox"
                                } catch (exc) {
                                    junit 'reports/junit-*.xml'
                                    error("Unit test Failed on Windows")
                                }
                            }
                        }
                    }
                    // "Linux": {
                    //     node(label: "Linux") {
                    //         script {
                    //             checkout scm
                    //             try {
                    //                 sh "${env.PYTHON3} -m tox"
                    //             } catch (exc) {
                    //                 junit 'reports/junit-*.xml'
                    //                 error("Unit test Failed on Linux")
                    //             }
                    //         }
                    //     }
                    // }
                )
                // parallel(
                //         "Windows": {
                //             script {
                //                 def runner = new Tox(this)
                //                 runner.windows = true
                //                 runner.stash = "Source"
                //                 runner.label = "Windows"
                //                 runner.post = {
                //                     junit 'reports/junit-*.xml'
                //                 }
                //                 runner.run()
                //             }
                //         },
                //         "Linux": {
                //             script {
                //                 def runner = new Tox(this)
                //                 runner.windows = false
                //                 runner.stash = "Source"
                //                 runner.label = "!Windows"
                //                 runner.post = {
                //                     junit 'reports/junit-*.xml'
                //                 }
                //                 runner.run()
                //             }
                //         }
                // )
            }
        }
        stage("Additional tests") {
            when {
                expression { params.ADDITIONAL_TESTS == true }
            }
            steps {
                parallel(
                        "MyPy": {
                            script {
                                def runner = new Tox(this)
                                runner.env = "mypy"
                                runner.windows = true
                                runner.stash = "Source"
                                runner.label = "Windows"
                                runner.post = {
                                    junit 'mypy.xml'
                                }
                                runner.run()

                            }
                        },
                        "Documentation": {
                            script {
                                def runner = new Tox(this)
                                runner.env = "docs"
                                runner.windows = true
                                runner.stash = "Source"
                                runner.label = "Windows"
                                runner.post = {
                                    dir('.tox/dist/html/') {
                                        stash includes: '**', name: "HTML Documentation", useDefaultExcludes: false
                                    }
                                }
                                runner.run()

                            }
                        },
                        "coverage": {
                            script {
                                def runner = new Tox(this)
                                runner.env = "coverage"
                                runner.windows = true
                                runner.stash = "Source"
                                runner.label = "Windows"
                                runner.post = {
                                    publishHTML target: [
                                            allowMissing         : false,
                                            alwaysLinkToLastBuild: false,
                                            keepAll              : true,
                                            reportDir            : "reports/cov_html",
                                            reportFiles          : "index.html",
                                            reportName           : "Coverage Report"
                                    ]
                                }
                                runner.run()

                            }
                        }
                )
            }
        }

        stage("Packaging") {
            when {
                expression { params.PACKAGE == true }
            }
            steps {
                parallel(
                    "Source and Wheel formats": {
                        bat """${tool 'Python3.6.3_Win64'} -m venv venv
                                call venv\\Scripts\\activate.bat
                                pip install -r requirements-dev.txt
                                python setup.py sdist bdist_wheel
                                """
                        dir("dist"){
                            archiveArtifacts artifacts: "*.whl", fingerprint: true
                            archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
                        }
                    },
                    "Windows CX_Freeze MSI": {
                        node(label: "Windows") {
                            deleteDir()
                            checkout scm
                            bat "${tool 'Python3.6.3_Win64'} -m venv venv"
                            bat "make freeze"
                            dir("dist") {
                                stash includes: "*.msi", name: "msi"
                                archiveArtifacts artifacts: "*.msi", fingerprint: true
                            }

                        }
                        node(label: "Windows") {
                            deleteDir()
                            git url: 'https://github.com/UIUCLibrary/ValidateMSI.git'
                            unstash "msi"
                            bat "call validate.bat -i"
                            
                        }
                    },
                    //     "Source Package": {
                    //         createSourceRelease(env.PYTHON3, "Source")
                    //     },
                    //     "Python Wheel:": {
                    //         node(label: "Windows") {
                    //             deleteDir()
                    //             unstash "Source"
                    //             withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                    //                 bat """
                    //   ${env.PYTHON3} -m venv .env
                    //   call .env/Scripts/activate.bat
                    //   pip install -r requirements.txt
                    //   python setup.py bdist_wheel
                    // """
                    //                 dir("dist") {
                    //                     archiveArtifacts artifacts: "*.whl", fingerprint: true
                    //                 }
                    //             }
                    //         }
                    //     },
                        // "Python CX_Freeze Windows": {
                        //     node(label: "Windows") {
                        //         deleteDir()
                        //         unstash "Source"
                        //         withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                        //             bat """
                        //                 ${env.PYTHON3} cx_setup.py bdist_msi --add-to-path=true
                        //                 """
                        //             dir("dist") {
                        //                 archiveArtifacts artifacts: "*.msi", fingerprint: true
                        //                 stash includes: "*.msi", name: "msi"
                        //             }
                        //         }
                        //     }
                        // }
                )
            }
        }
        stage("Update online documentation") {
            agent any
            when {
                expression { params.UPDATE_DOCS == true }
            }
            steps {
                updateOnlineDocs stash_name: "HTML Documentation", url_subdomain: params.URL_SUBFOLDER
            }
        }
        stage("Deploying to Devpi") {
            when {
                expression { params.DEPLOY_DEVPI == true }
            }
            steps {
                bat "${tool 'Python3.6.3_Win64'} -m devpi use http://devpy.library.illinois.edu"
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                    script {
                        bat "${tool 'Python3.6.3_Win64'} -m devpi upload --from-dir dist"
                        try {
                            bat "${tool 'Python3.6.3_Win64'} -m devpi upload --only-docs"
                        } catch (exc) {
                            echo "Unable to upload to devpi with docs."
                        }
                    }
                }

            }
        }
        stage("Test Devpi packages") {
            when {
                expression { params.DEPLOY_DEVPI == true }
            }
            steps {
                parallel(
                        "Source": {
                            script {
                                def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                                def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                                node("Windows") {
                                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                        bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                        bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                        echo "Testing Source package in devpi"
                                        script {
                                             def devpi_test = bat(returnStdout: true, script: "${tool 'Python3.6.3_Win64'} -m devpi test --index http://devpy.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name} -s tar.gz").trim()
                                             if(devpi_test =~ 'tox command failed') {
                                                error("Tox command failed")
                                            }
                                        }
                                    }
                                }

                            }
                        },
                        "Wheel": {
                            script {
                                def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                                def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                                node("Windows") {
                                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                        bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                        bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                        echo "Testing Whl package in devpi"
                                        script {
                                            def devpi_test =  bat(returnStdout: true, script: "${tool 'Python3.6.3_Win64'} -m devpi test --index http://devpy.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name} -s whl").trim()
                                            if(devpi_test =~ 'tox command failed') {
                                                error("Tox command failed")
                                            }
                                            
                                        }

                                    }
                                }

                            }
                        }
                )

            }
            post {
                success {
                    echo "it Worked. Pushing file to ${env.BRANCH_NAME} index"
                    script {
                        def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                        def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            bat "${tool 'Python3.6.3_Win64'} -m devpi push ${name}==${version} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                        }

                    }
                }
            }
        }
        stage("Deploy - Staging") {
            agent any
            when {
                expression { params.DEPLOY == true && params.PACKAGE == true }
            }
            steps {
                deployStash("msi", "${env.SCCM_STAGING_FOLDER}/${params.PROJECT_NAME}/")
                input("Deploy to production?")
            }
        }

        stage("Deploy - SCCM upload") {
            agent any
            when {
                expression { params.DEPLOY == true && params.PACKAGE == true }
            }
            steps {
                deployStash("msi", "${env.SCCM_UPLOAD_FOLDER}")
            }
            post {
                success {
                    script{
                        unstash "Source"
                        def  deployment_request = requestDeploy this, "deployment.yml"
                        echo deployment_request
                        writeFile file: "deployment_request.txt", text: deployment_request
                        archiveArtifacts artifacts: "deployment_request.txt"
                    }

                }
            }
        }
    }
}
