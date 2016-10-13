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
        sh 'make html -C ./docs -e ./dist/docs'
    }
    stage("Packaging source"){

        sh '$PYTHON3 setup.py sdist'
        archiveArtifacts artifacts: 'dist/*.tar.gz'

    }
}