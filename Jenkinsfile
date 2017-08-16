#!groovy
@Library("ds-utils")
import org.ds.*

pipeline {
    agent any
    environment {
        mypy_args = "--junit-xml=mypy.xml"
        pytest_args = "--junitxml=reports/junit-{env:OS:UNKNOWN_OS}-{envname}.xml --junit-prefix={env:OS:UNKNOWN_OS}  --basetemp={envtmpdir}"
    }
    parameters {
        string(name: "PROJECT_NAME", defaultValue: "Medusa Packager", description: "Name given to the project")
        booleanParam(name: "UNIT_TESTS", defaultValue: true, description: "Run Automated Unit Tests")
        booleanParam(name: "STATIC_ANALYSIS", defaultValue: true, description: "Run static analysis tests")
        booleanParam(name: "BUILD_DOCS", defaultValue: true, description: "Build documentation")
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
                            script {
                                def runner = new Tox(this)
                                runner.windows = true
                                runner.stash = "Source"
                                runner.label = "Windows"
                                runner.post = {
                                    junit 'reports/junit-*.xml'
                                }
                                runner.run()
                            }
                        },
                        "Linux": {
                            script {
                                def runner = new Tox(this)
                                runner.windows = false
                                runner.stash = "Source"
                                runner.label = "!Windows"
                                runner.post = {
                                    junit 'reports/junit-*.xml'
                                }
                                runner.run()
                            }
                        }
                )
            }
        }
        stage("Static Analysis") {
            when {
                expression { params.STATIC_ANALYSIS == true }
            }
            steps {
                parallel(
                        "MyPy": {
                            script {
                                def runner = new Tox(this)
                                runner.env = "mypy"
                                runner.windows = false
                                runner.stash = "Source"
                                runner.label = "!Windows"
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
                                runner.windows = false
                                runner.stash = "Source"
                                runner.label = "!Windows"
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
                                runner.windows = false
                                runner.stash = "Source"
                                runner.label = "!Windows"
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
//        stage("Documentation") {
//            agent any
//            when {
//                expression { params.BUILD_DOCS == true }
//            }
//            steps {
//                deleteDir()
//                unstash "Source"
//                withEnv(['PYTHON=${env.PYTHON3}']) {
//                    sh """
//                  ${env.PYTHON3} -m venv .env
//                  . .env/bin/activate
//                  pip install -r requirements.txt
//                  cd docs && make html
//
//                  """
//
//                    // dir('docs') {
//                    //     sh 'make html SPHINXBUILD=$SPHINXBUILD'
//                    // }
//                    dir("docs/build/html") {
//                        stash includes: '**', name: "Documentation source", useDefaultExcludes: false
//                    }
//
//
//                }
//            }
//            post {
//                success {
//                    sh 'tar -czvf sphinx_html_docs.tar.gz -C docs/build/html .'
//                    archiveArtifacts artifacts: 'sphinx_html_docs.tar.gz'
//                }
//            }
//        }
        stage("Packaging") {
            when {
                expression { params.PACKAGE == true }
            }
            steps {
                parallel(
                        "Source Package": {
                            createSourceRelease(env.PYTHON3, "Source")
                        },
                        "Python Wheel:": {
                            node(label: "Windows") {
                                deleteDir()
                                unstash "Source"
                                withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                                    bat """
                      ${env.PYTHON3} -m venv .env
                      call .env/Scripts/activate.bat
                      pip install -r requirements.txt
                      python setup.py bdist_wheel
                    """
                                    dir("dist") {
                                        archiveArtifacts artifacts: "*.whl", fingerprint: true
                                    }
                                }
                            }
                        },
                        "Python CX_Freeze Windows": {
                            node(label: "Windows") {
                                deleteDir()
                                unstash "Source"
                                withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                                    bat """
                      ${env.PYTHON3} cx_setup.py bdist_msi --add-to-path=true
                    """
                                    dir("dist") {
                                        archiveArtifacts artifacts: "*.msi", fingerprint: true
                                        stash includes: "*.msi", name: "msi"
                                    }
                                }
                            }
                        }
                )
            }
        }
        stage("Update online documentation") {
            agent any
            when {
                expression { params.UPDATE_DOCS == true }
            }
            steps {
                updateOnlineDocs stash_name: "Documentation source", url_subdomain: params.URL_SUBFOLDER
            }
        }
        stage("Deploy - Staging") {
            agent any
            when {
                expression { params.DEPLOY == true && params.PACKAGE == true }
            }
            steps {
                deleteDir()
                unstash "msi"
                sh "rsync -rv ./ \"${env.SCCM_STAGING_FOLDER}/${params.PROJECT_NAME}/\""
                input("Deploy to production?")
            }
        }

        stage("Deploy - SCCM upload") {
            agent any
            when {
                expression { params.DEPLOY == true && params.PACKAGE == true }
            }
            steps {
                deleteDir()
                unstash "msi"
                sh "rsync -rv ./ ${env.SCCM_UPLOAD_FOLDER}/"
            }
            post {
                success {
                    git url: 'https://github.com/UIUCLibrary/sccm_deploy_message_generator.git'
                    unstash "Deployment"
                    sh """${env.PYTHON3} -m venv .env
                  . .env/bin/activate
                  pip install --upgrade pip
                  pip install setuptools --upgrade
                  python setup.py install
                  deploymessage deployment.yml --save=deployment_request.txt
              """
                    archiveArtifacts artifacts: "deployment_request.txt"
                    echo(readFile('deployment_request.txt'))
                }
            }
        }
    }
}
