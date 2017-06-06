#!groovy
pipeline {
    agent any
    parameters {
      booleanParam(name: "UPDATE_DOCS", defaultValue: false, description: "Update the documentation")
    }

    stages {
        stage("Cloning Source") {
            agent any

            steps {
                deleteDir()
                echo "Cloning source"
                checkout scm
                stash includes: '**', name: "source"

            }
        }
        stage("Unit tests") {
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
                "Python Wheel:" :{
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
                "Python CX_Freeze Windows" :{
                  node(label: "Windows") {
                    deleteDir()
                    unstash "source"
                    withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                      bat """
                        ${env.PYTHON3} cx_setup.py bdist_msi --add-to-path=true
                      """
                      dir("dist") {
                        archiveArtifacts artifacts: "*.msi", fingerprint: true
                      }
                    }
                  }
                }
              )

            }
        }
         stage("Update online documentation") {
            agent any
            when{
              expression{params.UPDATE_DOCS == true}
            }

            steps {
                deleteDir()
                script {
                    unstash "Documentation source"
                    sh("scp -r -i ${env.DCC_DOCS_KEY} docs/build/html/* ${env.DCC_DOCS_SERVER}/DCCMedusaPackager/")


                }


            }

        }

    }
}
