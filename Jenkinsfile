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
                unstash "Source"
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
//         stage("Documentation") {
//             agent {
//                 label "!Windows"
//             }
//
//             steps {
//                 deleteDir()
//                 unstash "source"
// //                echo 'Building documentation'
// //                echo 'Creating virtualenv for generating docs'
//                 withEnv(['PYTHON=${env.PYTHON3}']) {
// //
//                     dir('docs') {
//                         sh 'make html SPHINXBUILD=$SPHINXBUILD'
//                     }
//                     stash includes: '**', name: "Documentation source", useDefaultExcludes: false
//
//                 }
// //                sh "${env.PYTHON3} -m virtualenv -p ${env.PYTHON3} venv_doc"
// //                sh '. ./venv_doc/bin/activate && \
// //                          pip install Sphinx && \
// //                          python setup.py build_sphinx'
//
//                 sh 'tar -czvf sphinx_html_docs.tar.gz -C docs/build/html .'
//                 archiveArtifacts artifacts: 'sphinx_html_docs.tar.gz'
//             }
//         }

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
                        ${env.PYTHON3} -m venv .env
                        call .env/Scripts/activate.bat

                        pip install -r requirements.txt
                        python cx_setup.py bdist_msi --add-to-path=true
                      """
                      //   python cx_setup.py build --build-exe build/tmp
                      //   build\\tmp\\qcpkg.exe --pytest --verbose  --junitxml=reports/junit-frozen.xml --junit-prefix=frozen
                      //   if %errorlevel%==0 (
                      //     python cx_setup.py bdist_msi --add-to-path=true
                      //     ) else (
                      //       echo errorlevel=%errorlevel%
                      //       exit /b %errorlevel%
                      //       )
                      // """
                      // junit 'reports/junit-*.xml'
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
