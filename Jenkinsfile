#!groovy
pipeline {
    agent any

    stages {
        stage("Cloning Source") {
            agent any

            steps {
                deleteDir()
                echo "Cloning source"
                checkout scm
                stash includes: '**', name: "Source"

            }
        }
        stage("Unit tests") {
            steps {
                parallel(
                        "Windows": {
                            node(label: 'Windows') {
                                deleteDir()
                                unstash "Source"
                                echo "Running Tox: Python 3.5 Unit tests"
                                bat "${env.TOX}  --skip-missing-interpreters"
                                junit 'reports/junit-*.xml'

                            }
                        },
                        "Linux": {
                            node(label: "!Windows") {
                                deleteDir()
                                unstash "Source"
                                echo "Running Tox: Unit tests"
                                withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {

                                    echo "PATH = ${env.PATH}"
                                    echo "Running: ${env.TOX}  --skip-missing-interpreters -e py35"
                                    sh "${env.TOX}  --skip-missing-interpreters -e py35"
                                }
                                junit 'reports/junit-*.xml'
                            }
                        }
                )
            }
        }
        stage("Static Analysis") {
            steps {
                parallel(
                        "mypy": {
                            node(label: "!Windows") {
                                deleteDir()
                                unstash "Source"
                                sh "${env.TOX} -e mypy"
                                publishHTML target: [
                                        allowMissing         : false,
                                        alwaysLinkToLastBuild: false,
                                        keepAll              : true,
                                        reportDir            : "mypy_report",
                                        reportFiles          : "index.html",
                                        reportName           : "MyPy Report"
                                ]
                            }
                        },
                        "coverage": {
                            node(label: "!Windows") {
                                deleteDir()
                                unstash "Source"
                                sh "${env.TOX} -e coverage"
                                publishHTML target: [
                                        allowMissing         : false,
                                        alwaysLinkToLastBuild: false,
                                        keepAll              : true,
                                        reportDir            : "htmlcov",
                                        reportFiles          : "index.html",
                                        reportName           : "Coverage Report"
                                ]
                            }
                        }
                )
            }
        }
        stage("Documentation") {
            agent {
                label "!Windows"
            }

            steps {
                deleteDir()
                unstash "Source"
                echo 'Building documentation'
                echo 'Creating virtualenv for generating docs'
                sh "${env.PYTHON3} -m virtualenv -p ${env.PYTHON3} venv_doc"
                sh '. ./venv_doc/bin/activate && \
                          pip install Sphinx && \
                          python setup.py build_sphinx'

                sh 'tar -czvf sphinx_html_docs.tar.gz -C docs/build/html .'
                archiveArtifacts artifacts: 'sphinx_html_docs.tar.gz'
            }
        }

        stage("Packaging") {
            steps {
                parallel(
                        "Windows Wheel": {
                            node(label: "Windows") {
                                deleteDir()
                                unstash "Source"
                                bat "${env.PYTHON3} setup.py bdist_wheel --universal"
                                archiveArtifacts artifacts: "dist/**", fingerprint: true
                            }
                        },
                        "Source Release": {
                            deleteDir()
                            unstash "Source"
                            sh "${env.PYTHON3} setup.py sdist"
                            archiveArtifacts artifacts: "dist/**", fingerprint: true
                        }
                )
            }
        }

    }
}
