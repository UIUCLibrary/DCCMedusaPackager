#!groovy

node {
    stage('Pulling from Github'){
        checkout scm
        stash includes: '*', name: 'pysource'
    }
}



node {

    stage("Running Tox: Python 3.5 Unit tests"){
        env.PATH = "${env.PYTHON3}/..:${env.PATH}"
        unstash 'pysource'
        sh '$TOX -e py35'
        junit '**/junit-*.xml'


    }
}
stage("Running static static analysis reports") {
  parallel coverage: {
      echo "Running Coverage"
      runTox("coverage", "htmlcov", 'index.html', "Coverage Report")
    }, mypy: {
        echo "MyPy"
        runTox("mypy", "mypy_report", 'index.html', "MyPy Report")
      }
}

def runTox(environment, reportDir, reportFiles, reportName)
{
    node {
      unstash 'pysource'
      String command = "$TOX -e ${environment}"
      echo command
      sh command
      publishHTML([allowMissing: false,
                   alwaysLinkToLastBuild: false,
                   keepAll: false,
                   reportDir: "${reportDir}",
                   reportFiles: "${reportFiles}",
                   reportName: "${reportName}"])
    }
}

node {
    try {
        stage("Generating Documentation for Archive"){
            unstash 'pysource'
            echo 'Creating virtualenv for generating docs'
            sh '$PYTHON3 -m virtualenv -p $PYTHON3 venv_doc'
            sh '. ./venv_doc/bin/activate && \
            pip install Sphinx && \
            python setup.py build_sphinx'

            dir('docs/build'){
                stash includes: '**', name: 'sphinx_docs'
            }
        }

        stage("Archiving Documentation"){
            unstash 'sphinx_docs'
            sh 'tar -czvf sphinx_docs.tar.gz html'
            archiveArtifacts artifacts: 'sphinx_docs.tar.gz'
        }

        /* Turning this off until I can get git creds set up for jenkins server
        stage("Building and updating documentation for github pages") {
            unstash 'pysource'
            sh '$PYTHON3 -m virtualenv -p $PYTHON3 venv_doc'
            sh '. ./venv_doc/bin/activate && \
            pip install Sphinx && sh publishDocs.sh'
        }
        */

    } catch(error) {
        echo 'Unable to generate Sphinx documentation'
    }
}

node{
    stage("Building source distribution"){
        unstash 'pysource'
        sh '$PYTHON3 setup.py sdist'
        archiveArtifacts artifacts: 'dist/*.tar.gz'

    }
}
