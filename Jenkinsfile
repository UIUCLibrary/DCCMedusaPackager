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


    try{
        stage("Building documentation"){
            unstash 'pysource'
            echo 'Creating virtualenv for generating docs'
            sh '$PYTHON3 -m virtualenv -p $PYTHON3 venv_doc'
            sh '. ./venv_doc/bin/activate && \
            pip install Sphinx && \
            python setup.py build_sphinx'
            dir('docs/build'){
                stash includes: '**', name: 'sphinx_docs'
            }
        } catch (error) {
            echo 'Unable to build build_sphinx documentation.'
        }
    }
}
node{
    stage("Building source distribution"){
        try{
        unstash 'sphinx_docs'
        }
        unstash 'pysource'
        sh '$PYTHON3 setup.py sdist'
        archiveArtifacts artifacts: 'dist/*.tar.gz'

    }
}