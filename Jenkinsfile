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
        stage("Unit tests on Linux") {
            agent any

            steps {
                deleteDir()
                unstash "Source"
                echo "Running Tox: Unit tests"
                withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {

                    echo "PATH = ${env.PATH}"
                    echo "Running: ${env.TOX}  --skip-missing-interpreters"
                    sh "${env.TOX}  --skip-missing-interpreters"
                }

            }

            post {
                always {
                    stash includes: "reports/*.xml", name: "Linux junit"
                }

            }
        }
        stage("Unit tests on Windows") {
            agent {
                label "Windows"
            }

            steps {
                deleteDir()
                unstash "Source"
                echo "Running Tox: Python 3.5 Unit tests"
                bat "${env.TOX}  --skip-missing-interpreters"

            }
            post {
                always {
                    stash includes: "reports/*.xml", name: "Windows junit"

                }
            }

        }

        stage("mypy") {
            agent any
            steps {
                deleteDir()
                unstash "Source"
                sh "${env.TOX} -e coverage"
            }
            post {
                success {

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
        }
        stage("Coverage") {
            agent any
            steps {
                deleteDir()
                unstash "Source"
                sh "${env.TOX} -e mypy"
            }
            post {
                success {

                    publishHTML target: [
                            allowMissing         : false,
                            alwaysLinkToLastBuild: false,
                            keepAll              : true,
                            reportDir            : "mypy_report",
                            reportFiles          : "index.html",
                            reportName           : "MyPy Report"
                    ]
                }

            }
        }

        stage("Documentation") {
            agent any

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

//node {
//    stage('Pulling from Github'){
//        checkout scm
//        stash includes: '*', name: 'pysource'
//    }
//}

//node {
//
//    stage("Running Tox: Python 3.5 Unit tests"){
//        env.PATH = "${env.PYTHON3}/..:${env.PATH}"
//        unstash 'pysource'
//        sh '$TOX -e py35'
//        junit '**/junit-*.xml'
//
//
//    }
//}

//parallel coverage: {
//    echo "Running Coverage report"
//    runTox("coverage", "htmlcov", 'index.html', "Coverage Report")
//}, mypy: {
//    echo "Running MyPy report"
//    runTox("mypy", "mypy_report", 'index.html', "MyPy Report")
//}
//
//parallel documentation: {
//    node {
//        echo 'Building documentation'
//        try {
//            stage("Generating Documentation for Archive") {
//                unstash 'pysource'
//                echo 'Creating virtualenv for generating docs'
//                sh '$PYTHON3 -m virtualenv -p $PYTHON3 venv_doc'
//                sh '. ./venv_doc/bin/activate && \
//              pip install Sphinx && \
//              python setup.py build_sphinx'
//
//                dir('docs/build') {
//                    stash includes: '**', name: 'sphinx_docs'
//                }
//            }
//
//            stage("Archiving Documentation") {
//                unstash 'sphinx_docs'
//                sh 'tar -czvf sphinx_docs.tar.gz html'
//                archiveArtifacts artifacts: 'sphinx_docs.tar.gz'
//            }
//
//            /* Turning this off until I can get git creds set up for jenkins server
//            stage("Building and updating documentation for github pages") {
//                unstash 'pysource'
//                sh '$PYTHON3 -m virtualenv -p $PYTHON3 venv_doc'
//                sh '. ./venv_doc/bin/activate && \
//                pip install Sphinx && sh publishDocs.sh'
//            }
//            */
//
//        } catch (error) {
//            echo 'Unable to generate Sphinx documentation'
//        }
//    }
//}, sourceDist: {
//    node {
//        echo 'Building source distribution'
//        stage("Building source distribution") {
//            unstash 'pysource'
//            sh '$PYTHON3 setup.py sdist'
//            archiveArtifacts artifacts: 'dist/*.tar.gz'
//
//        }
//    }
//}

//def runTox(environment, reportDir, reportFiles, reportName) {
//    stage("Running ${reportName}") {
//        node {
//            unstash 'pysource'
//            sh "${env.TOX} -e ${environment}"
//            publishHTML([allowMissing         : false,
//                         alwaysLinkToLastBuild: false,
//                         keepAll              : false,
//                         reportDir            : "${reportDir}",
//                         reportFiles          : "${reportFiles}",
//                         reportName           : "${reportName}"])
//        }
//
//    }
//}
