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
                            echo "I'm running mypy"
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
                        },
                        "coverage": {
                            echo "I'm running coverage"
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

                sh 'tar -czvf sphinx_docs.tar.gz docs/build/html'
                stash includes: 'docs/build/**', name: 'sphinx_docs'
                archiveArtifacts artifacts: 'sphinx_docs.tar.gz'
            }
        }


        stage("Packaging source") {
            agent any

            steps {
                deleteDir()
                unstash "Source"
                sh "${env.PYTHON3} setup.py sdist"
            }

            post {
                success {
                    archiveArtifacts artifacts: "dist/**", fingerprint: true
                }
            }

        }

        stage("Packaging Windows binary Wheel") {
            agent {
                label "Windows"
            }

            steps {
                deleteDir()
                unstash "Source"
                bat "${env.PYTHON3} setup.py bdist_wheel --universal"
            }
            post {
                success {
                    archiveArtifacts artifacts: "dist/**", fingerprint: true
                }
            }

        }
    }
}
