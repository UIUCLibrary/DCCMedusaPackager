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


    stage("Building documentation"){
        unstash 'pysource'
        try{
            sh '$PYTHON3 setup.py build_sphinx'
        } catch (error) {
            echo 'Unable to build build_sphinx documentation.'
        }
    }

    stage("Building source distribution"){
        sh '$PYTHON3 setup.py sdist'
        archiveArtifacts artifacts: 'dist/*.tar.gz'

    }
}