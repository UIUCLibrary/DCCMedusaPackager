#!groovy
@Library("ds-utils")
import org.ds.*
pipeline {
    agent any
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
                stash includes: '**', name: "source"
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
                            node(label: 'Windows') {
                                deleteDir()
                                unstash "source"
                                withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                                    bat """
                          ${env.PYTHON3} -m venv .env
                                          call .env/Scripts/activate.bat
                                          pip install --upgrade setuptools
                                          pip install -r requirements.txt
                                          tox  --skip-missing-interpreters
                          """
                                }
                                junit 'reports/junit-*.xml'

                            }
                        },
                        "Linux": {
                            node(label: "!Windows") {
                                deleteDir()
                                unstash "source"
                                withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                                    sh """
                          ${env.PYTHON3} -m venv .env
                          . .env/bin/activate
                          pip install -r requirements.txt
                          tox  --skip-missing-interpreters -e py35 || true
                          """
                                }
                                junit 'reports/junit-*.xml'
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
                        "mypy": {
                            node(label: "!Windows") {
                                deleteDir()
                                unstash "source"
                                withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                                    sh """
                          ${env.PYTHON3} -m venv .env
                          . .env/bin/activate
                          pip install -r requirements.txt
                          tox  --skip-missing-interpreters -e mypy || true
                          """
                                }
                                // sh "${env.TOX} -e mypy"
                                publishHTML target: [
                                        allowMissing         : false,
                                        alwaysLinkToLastBuild: false,
                                        keepAll              : true,
                                        reportDir            : "reports/mypy_report",
                                        reportFiles          : "index.html",
                                        reportName           : "MyPy Report"
                                ]
                            }
                        },
                        "coverage": {
                            node(label: "!Windows") {
                                deleteDir()
                                unstash "source"
                                withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                                    sh """
                          ${env.PYTHON3} -m venv .env
                          . .env/bin/activate
                          pip install -r requirements.txt
                          tox  --skip-missing-interpreters -e coverage || true
                          """
                                }
                                // sh "${env.TOX} -e coverage"
                                publishHTML target: [
                                        allowMissing         : false,
                                        alwaysLinkToLastBuild: false,
                                        keepAll              : true,
                                        reportDir            : "reports/cov_html",
                                        reportFiles          : "index.html",
                                        reportName           : "Coverage Report"
                                ]
                            }
                        }
                )
            }
        }
        stage("Documentation") {
            agent any
            when {
                expression { params.BUILD_DOCS == true }
            }
            steps {
                deleteDir()
                unstash "source"
                withEnv(['PYTHON=${env.PYTHON3}']) {
                    sh """
                  ${env.PYTHON3} -m venv .env
                  . .env/bin/activate
                  pip install -r requirements.txt
                  cd docs && make html

                  """

                    // dir('docs') {
                    //     sh 'make html SPHINXBUILD=$SPHINXBUILD'
                    // }
                    stash includes: '**', name: "Documentation source", useDefaultExcludes: false
                }
            }
            post {
                success {
                    sh 'tar -czvf sphinx_html_docs.tar.gz -C docs/build/html .'
                    archiveArtifacts artifacts: 'sphinx_html_docs.tar.gz'
                }
            }
        }
        stage("Packaging") {
            when {
                expression { params.PACKAGE == true }
            }
            steps {
                parallel(
                        "Source Package": {
                            node(label: "!Windows") {
                                deleteDir()
                                unstash "source"
                                withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                                    sh """
                    ${env.PYTHON3} -m venv .env
                    . .env/bin/activate
                    pip install -r requirements.txt
                    python setup.py sdist
                    """
                                    dir("dist") {
                                        archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
                                    }
                                }
                            }
                        },
                        "Python Wheel:": {
                            node(label: "Windows") {
                                deleteDir()
                                unstash "source"
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
                                unstash "source"
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
                expression { params.UPDATE_DOCS == true && params.BUILD_DOCS == true }
            }
            steps {
                updateOnlineDocs stash_name: "Documentation source", url_subdomain: params.URL_SUBFOLDER
//                deleteDir()
//                script {
//                    unstash "Documentation source"
//                    try {
//                        sh("rsync -rv -e \"ssh -i ${env.DCC_DOCS_KEY}\" docs/build/html/ ${env.DCC_DOCS_SERVER}/${params.URL_SUBFOLDER}/ --delete")
//                    } catch (error) {
//                        echo "Error with uploading docs"
//                        throw error
//                    }
//                }
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
