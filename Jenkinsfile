node {
    stage('Pulling from Github'){
        checkout scm
        stash includes: '*', name: 'pysource'
    }
}

node {

    stage("Running Tox"){
        unstash 'pysource'
        sh '$TOX'
        junit '**/junit-*.xml'
    }
}

node {
    try {
        stage("Generating Documentation"){
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

        stage("Packaging Documentation"){
            unstash 'sphinx_docs'
            sh 'tar -czvf sphinx_docs.tar.gz html'
            archiveArtifacts artifacts: 'sphinx_docs.tar.gz'
        }

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