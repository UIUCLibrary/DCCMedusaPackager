#!groovy
@Library("ds-utils")
import org.ds.*

@Library(["devpi", "PythonHelpers"]) _
// ============================================================================
// Versions of python that are supported
// ----------------------------------------------------------------------------
SUPPORTED_MAC_VERSIONS = ['3.8', '3.9']
SUPPORTED_LINUX_VERSIONS = [ '3.7', '3.8', '3.9']
SUPPORTED_WINDOWS_VERSIONS = [ '3.7', '3.8', '3.9']

def getDevPiStagingIndex(){

    if (env.TAG_NAME?.trim()){
        return "tag_staging"
    } else{
        return "${env.BRANCH_NAME}_staging"
    }
}

DEVPI_CONFIG = [
    index: getDevPiStagingIndex(),
    server: 'https://devpi.library.illinois.edu',
    credentialsId: 'DS_devpi',
]
defaultParameterValues = [
    USE_SONARQUBE: false
]

def remove_from_devpi(devpiExecutable, pkgName, pkgVersion, devpiIndex, devpiUsername, devpiPassword){
    script {
                try {
                    bat "${devpiExecutable} login ${devpiUsername} --password ${devpiPassword}"
                    bat "${devpiExecutable} use ${devpiIndex}"
                    bat "${devpiExecutable} remove -y ${pkgName}==${pkgVersion}"
                } catch (Exception ex) {
                    echo "Failed to remove ${pkgName}==${pkgVersion} from ${devpiIndex}"
            }

    }
}

def get_package_version(stashName, metadataFile){
    ws {
        unstash "${stashName}"
        script{
            def props = readProperties interpolate: true, file: "${metadataFile}"
            deleteDir()
            return props.Version
        }
    }
}

def get_package_name(stashName, metadataFile){
    ws {
        unstash "${stashName}"
        script{
            def props = readProperties interpolate: true, file: "${metadataFile}"
            deleteDir()
            return props.Name
        }
    }
}

def startup(){
    stage("Getting Distribution Info"){
        node('linux && docker') {
            timeout(2){
                ws{
                    checkout scm
                    try{
                        docker.image('python').inside {
                            sh(
                               label: "Running setup.py with dist_info",
                               script: """python --version
                                          python setup.py dist_info
                                       """
                            )
                            stash includes: "*.dist-info/**", name: 'DIST-INFO'
                            archiveArtifacts artifacts: "*.dist-info/**"
                        }
                    } finally{
                        deleteDir()
                    }
                }
            }
        }
    }
}
def get_props(){
    stage('Reading Package Metadata'){
        node(){
            unstash 'DIST-INFO'
            def metadataFile = findFiles( glob: '*.dist-info/METADATA')[0]
            def metadata = readProperties(interpolate: true, file: metadataFile.path )
            echo """Version = ${metadata.Version}
Name = ${metadata.Name}
"""
            return metadata
        }
    }
}


startup()
props = get_props()

pipeline {
    agent none
    parameters {
        string(name: "PROJECT_NAME", defaultValue: "Medusa Packager", description: "Name given to the project")
        booleanParam(name: "PACKAGE_CX_FREEZE", defaultValue: false, description: "Create a package with CX_Freeze")
        booleanParam(name: "TEST_RUN_TOX", defaultValue: false, description: "Run Tox Tests")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: false, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to https://devpi.library.illinois.edu/production/release")
        booleanParam(name: "DEPLOY_SCCM", defaultValue: false, description: "Request deployment of MSI installer to SCCM")
        booleanParam(name: "UPDATE_DOCS", defaultValue: false, description: "Update the documentation")
        string(name: 'URL_SUBFOLDER', defaultValue: "DCCMedusaPackager", description: 'The directory that the docs should be saved under')
    }
    stages {
        stage("Getting Distribution Info"){
           agent {
                dockerfile {
                    filename 'ci/docker/python/linux/jenkins/Dockerfile'
                    label 'linux && docker'
                }
            }
            steps{
                sh "python setup.py dist_info"
            }
            post{
                success{
                    stash includes: "MedusaPackager.dist-info/**", name: 'DIST-INFO'
                    archiveArtifacts artifacts: "MedusaPackager.dist-info/**"
                }
            }
        }
        stage("Building") {
            stages{
                stage("Building Python Package"){
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker'
                        }
                    }
                    steps {
                        sh(label: "Building Python package",
                           script: """mkdir -p logs
                                      python setup.py build -b build  | tee logs/build.log
                                      """
                       )
//                         powershell "& ${WORKSPACE}\\venv\\Scripts\\python.exe setup.py build -b ${WORKSPACE}\\build  | tee ${WORKSPACE}\\logs\\build.log"

                    }
                    post{
                        always{
                            archiveArtifacts artifacts: "logs/build.log"
                            recordIssues(tools: [
                                        pyLint(name: 'Setuptools Build: PyLint', pattern: 'logs/build.log'),
                                        msBuild(name: 'Setuptools Build: MSBuild', pattern: 'logs/build.log')
                                    ]
                                )
                        }
                    }
                }
                stage("Building Sphinx Documentation"){
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker'
                        }
                    }
                    environment{
                        PKG_NAME = get_package_name("DIST-INFO", "MedusaPackager.dist-info/METADATA")
                        PKG_VERSION = get_package_version("DIST-INFO", "MedusaPackager.dist-info/METADATA")
                    }

                    steps {
                            sh (
                                label: "Building docs on ${env.NODE_NAME}",
                                script: """mkdir -p logs
                                           python -m sphinx docs/source build/docs/html -d build/docs/.doctrees -v -w logs/build_sphinx.log
                                           """
                            )
                    }
                    post{
                        always {
                            recordIssues(tools: [sphinxBuild(name: 'Sphinx Documentation Build', pattern: 'logs/build_sphinx.log', id: 'sphinx_build')])
                            archiveArtifacts artifacts: 'logs/build_sphinx.log'
                        }
                        success{
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                            script{
                                def DOC_ZIP_FILENAME = "${env.PKG_NAME}-${env.PKG_VERSION}.doc.zip"
                                zip archive: true, dir: "build/docs/html", glob: '', zipFile: "dist/${DOC_ZIP_FILENAME}"
                                stash includes: "dist/${DOC_ZIP_FILENAME},build/docs/html/**", name: 'DOCS_ARCHIVE'
                            }
                        }
                        failure{
                            echo "Failed to build Python package"
                        }
                    }
                }
            }
        }
        stage("Checks"){
            stages{
                stage("Code Quality") {
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker'
                        }
                    }
                    stages{
                        stage('Run Tests'){
                            parallel {
                                stage("PyTest"){
                                    steps{
                                        sh "python -m pytest --junitxml=reports/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:reports/coverage/ --cov=MedusaPackager" //  --basetemp={envtmpdir}"
                                    }
                                    post {
                                        always{
                                            junit "reports/junit-${env.NODE_NAME}-pytest.xml"
                                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/coverage', reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                                        }
                                    }
                                }
                                stage("MyPy"){
                                    steps{
                                        sh "mypy -p MedusaPackager --junit-xml=junit-${env.NODE_NAME}-mypy.xml --html-report reports/mypy_html"
                                    }
                                    post{
                                        always {
                                            junit "junit-${env.NODE_NAME}-mypy.xml"
                                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy_html', reportFiles: 'index.html', reportName: 'MyPy', reportTitles: ''])
                                        }
                                    }
                                }
                                stage("Documentation"){
                                    steps{
                                            sh """mkdir -p logs
                                                  python -m sphinx -b doctest docs/source build/docs -d build/docs/doctrees -v -w logs/doctest.log --no-color
                                                  """
                                    }
                                    post{
                                        always {
                                            recordIssues(tools: [sphinxBuild(pattern: 'logs/doctest.log')])

                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                stage("Run Tox"){
                    when{
                        equals expected: true, actual: params.TEST_RUN_TOX
                    }
                    steps {
                        script{
                            def tox
                            node(){
                                checkout scm
                                tox = load("ci/jenkins/scripts/tox.groovy")
                            }
                            def windowsJobs = [:]
                            def linuxJobs = [:]
                            stage("Scanning Tox Environments"){
                                parallel(
                                    "Linux Tox Scanning":{
                                        linuxJobs = tox.getToxTestsParallel(
                                                stagePrefix: "Tox Linux",
                                                label: "linux && docker",
                                                dockerfile: "ci/docker/python/linux/tox/Dockerfile",
                                                dockerBuildArgs: "--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL"
                                            )
                                    },
                                    "Windows Tox Scanning":{
                                        windowsJobs = tox.getToxTestsParallel(
                                                stagePrefix: "Tox Windows",
                                                label: "windows && docker",
                                                dockerfile: "ci/docker/python/windows/tox/Dockerfile",
                                                dockerBuildArgs: "--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE"
                                            )
                                    },
                                    failFast: true
                                )
                            }
                            parallel(windowsJobs + linuxJobs)
                        }
                    }
                }
            }
        }
        stage("Packaging") {
            parallel {
                stage("Source and Wheel Formats"){
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker'
                        }
                    }
                    steps{
                        sh "python setup.py sdist -d dist bdist_wheel -d dist"
                    }
                    post{
                        success{
                                archiveArtifacts artifacts: "dist/*.whl,dist/*.tar.gz,dist/*.zip", fingerprint: true
                                stash includes: "dist/*.whl,dist/*.tar.gz,dist/*.zip", name: 'PYTHON_PACKAGES'
                        }
                    }
                }
                stage("Windows CX_Freeze MSI"){
                    when{
                        equals expected: true, actual: params.PACKAGE_CX_FREEZE
                        beforeAgent true
                    }
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/windows/jenkins/Dockerfile'
                            label "windows && docker"
                        }
                    }
                    steps{
                        timeout(10){
                            bat(
                                label: "Freezing to msi installer",
                                script:"python cx_setup.py bdist_msi --add-to-path=true -k --bdist-dir build/msi -d dist"
                                )
                        }


                    }
                    post{
                        success{
                            dir("dist") {
                                stash includes: "*.msi", name: "msi"
                            }
                            archiveArtifacts artifacts: "dist/*.msi", fingerprint: true
                        }
                    }
                }
            }
        }
        stage("Deploy to DevPi") {
            when {
                allOf{
                    anyOf{
                        equals expected: true, actual: params.DEPLOY_DEVPI
                    }
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                        tag "*"
                    }
                }
                beforeAgent true
            }
            options{
                timestamps()
            }
            stages{
                stage("Deploy to Devpi Staging") {
                    agent {
                        dockerfile {
                            filename 'ci/docker/deploy/devpi/deploy/Dockerfile'
                            label 'linux&&docker'
                            additionalBuildArgs '--build-arg PIP_INDEX_URL --build-arg PIP_EXTRA_INDEX_URL'
                          }
                    }
                    steps {
                        unstash 'DOCS_ARCHIVE'
                        unstash 'PYTHON_PACKAGES'
                        script{
                            def devpi = load('ci/jenkins/scripts/devpi.groovy')
                            devpi.upload(
                                    server: DEVPI_CONFIG.server,
                                    credentialsId: DEVPI_CONFIG.credentialsId,
                                    index: DEVPI_CONFIG.index,
                                    clientDir: './devpi'
                                )
                        }
                    }
                    post{
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: "dist/", type: 'INCLUDE'],
                                    [pattern: "devpi/", type: 'INCLUDE'],
                                    [pattern: 'build/', type: 'INCLUDE']
                                ]
                            )
                        }
                    }
                }
                stage("Test DevPi Packages") {
                    steps{
                        script{
                            def devpi
                            node(){
                                checkout scm
                                devpi = load('ci/jenkins/scripts/devpi.groovy')
                            }
                             def macPackages = [:]
                            SUPPORTED_MAC_VERSIONS.each{pythonVersion ->
                                macPackages["Test Python ${pythonVersion}: wheel Mac"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            label: "mac && python${pythonVersion}"
                                        ],
                                        devpi: [
                                            index: DEVPI_CONFIG.index,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,
                                            devpiExec: 'venv/bin/devpi'
                                        ],
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: 'whl'
                                        ],
                                        test:[
                                            setup: {
                                                sh(
                                                    label:'Installing Devpi client',
                                                    script: '''python3 -m venv venv
                                                                venv/bin/python -m pip install pip --upgrade
                                                                venv/bin/python -m pip install devpi_client
                                                                '''
                                                )
                                            },
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                            teardown: {
                                                sh( label: 'Remove Devpi client', script: 'rm -r venv')
                                            }
                                        ]
                                    )
                                }
                                macPackages["Test Python ${pythonVersion}: sdist Mac"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            label: "mac && python${pythonVersion}"
                                        ],
                                        devpi: [
                                            index: DEVPI_CONFIG.index,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,
                                            devpiExec: 'venv/bin/devpi'
                                        ],
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: 'tar.gz'
                                        ],
                                        test:[
                                            setup: {
                                                checkout scm
                                                sh(
                                                    label:'Installing Devpi client',
                                                    script: '''python3 -m venv venv
                                                                venv/bin/python -m pip install pip --upgrade
                                                                venv/bin/python -m pip install devpi_client
                                                                '''
                                                )
                                            },
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                            teardown: {
                                                sh( label: 'Remove Devpi client', script: 'rm -r venv')
                                            }
                                        ]
                                    )
                                }
                            }
                            windowsPackages = [:]
                            SUPPORTED_WINDOWS_VERSIONS.each{pythonVersion ->
                                windowsPackages["Test Python ${pythonVersion}: sdist Windows"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            dockerfile: [
                                                filename: 'ci/docker/python/windows/tox/Dockerfile',
                                                additionalBuildArgs: "--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE",
                                                label: 'windows && docker'
                                            ]
                                        ],
                                        devpi: DEVPI_CONFIG,
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: 'tar.gz'
                                        ],
                                        test:[
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                        ]
                                    )
                                }
                                windowsPackages["Test Python ${pythonVersion}: wheel Windows"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            dockerfile: [
                                                filename: 'ci/docker/python/windows/tox/Dockerfile',
                                                additionalBuildArgs: "--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE",
                                                label: 'windows && docker'
                                            ]
                                        ],
                                        devpi: DEVPI_CONFIG,
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: 'whl'
                                        ],
                                        test:[
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                        ]
                                    )
                                }
                            }
                            def linuxPackages = [:]
                            SUPPORTED_LINUX_VERSIONS.each{pythonVersion ->
                                linuxPackages["Test Python ${pythonVersion}: sdist Linux"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            dockerfile: [
                                                filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                additionalBuildArgs: "--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL",
                                                label: 'linux && docker'
                                            ]
                                        ],
                                        devpi: DEVPI_CONFIG,
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: 'tar.gz'
                                        ],
                                        test:[
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                        ]
                                    )
                                }
                                linuxPackages["Test Python ${pythonVersion}: wheel Linux"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            dockerfile: [
                                                filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                label: 'linux && docker'
                                            ]
                                        ],
                                        devpi: DEVPI_CONFIG,
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: 'whl'
                                        ],
                                        test:[
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                        ]
                                    )
                                }
                            }
                            parallel(linuxPackages + windowsPackages + macPackages)
                        }
                    }
                }
                stage("Deploy to DevPi Production") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                            anyOf{
                                branch "master"
                                tag "*"
                            }
                        }
                        beforeAgent true
                        beforeInput true
                    }
                    options{
                        lock("uiucprescon.packager-devpi")
                    }
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/tox/Dockerfile'
                            label 'linux&&docker'
                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                          }
                    }
                    input {
                        message 'Release to DevPi Production?'
                    }
                    steps {
                        script{
                            def devpi = load('ci/jenkins/scripts/devpi.groovy')
                            devpi.pushPackageToIndex(
                                pkgName: props.Name,
                                pkgVersion: props.Version,
                                server: DEVPI_CONFIG.server,
                                indexSource: DEVPI_CONFIG.index,
                                indexDestination: 'production/release',
                                credentialsId: DEVPI_CONFIG.credentialsId
                            )
                        }
                    }
                }
            }
            post{
                success{
                    node('linux && docker') {
                        checkout scm
                        script{
                            if (!env.TAG_NAME?.trim()){
                                docker.build("dccmeduspackager:devpi",'-f ./ci/docker/python/linux/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL .').inside{
                                    def devpi = load('ci/jenkins/scripts/devpi.groovy')
                                    devpi.pushPackageToIndex(
                                        pkgName: props.Name,
                                        pkgVersion: props.Version,
                                        server: DEVPI_CONFIG.server,
                                        indexSource: DEVPI_CONFIG.index,
                                        indexDestination: "DS_Jenkins/${env.BRANCH_NAME}",
                                        credentialsId: DEVPI_CONFIG.credentialsId
                                    )
                                }
                            }
                        }
                    }
                }
                cleanup{
                    node('linux && docker') {
                       script{
                            checkout scm
                            docker.build("dccmeduspackager:devpi",'-f ci/docker/python/linux/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL .').inside{
                                def devpi = load('ci/jenkins/scripts/devpi.groovy')
                                devpi.removePackage(
                                    pkgName: props.Name,
                                    pkgVersion: props.Version,
                                    index: DEVPI_CONFIG.index,
                                    server: DEVPI_CONFIG.server,
                                    credentialsId: DEVPI_CONFIG.credentialsId,
                                )
                            }
                       }
                    }
                }
            }
        }
        stage("Deploy to SCCM") {
            when {
                equals expected: true, actual: params.DEPLOY_SCCM
            }

            steps {
                node("Linux"){
                    unstash "msi"
                    deployStash("msi", "${env.SCCM_STAGING_FOLDER}/${params.PROJECT_NAME}/")
                    input("Push a SCCM release?")
                    deployStash("msi", "${env.SCCM_UPLOAD_FOLDER}")
                    deleteDir()
                }

            }
            post {
                success {
                    script{
                        def  deployment_request = requestDeploy this, "deployment.yml"
                        echo deployment_request
                        writeFile file: "deployment_request.txt", text: deployment_request
                        archiveArtifacts artifacts: "deployment_request.txt"
                    }
                }
            }
        }

        stage("Update Online Documentation") {
            agent any
            when {
                equals expected: true, actual: params.UPDATE_DOCS
            }
            options {
                skipDefaultCheckout(true)
            }
            steps {
                unstash 'DOCS_ARCHIVE'
                dir("build/docs/html/"){
                    bat "dir /s /B"
                    sshPublisher(
                        publishers: [
                            sshPublisherDesc(
                                configName: 'apache-ns - lib-dccuser-updater', 
                                sshLabel: [label: 'Linux'], 
                                transfers: [sshTransfer(excludes: '', 
                                execCommand: '', 
                                execTimeout: 120000, 
                                flatten: false, 
                                makeEmptyDirs: false, 
                                noDefaultExcludes: false, 
                                patternSeparator: '[, ]+', 
                                remoteDirectory: "${params.URL_SUBFOLDER}", 
                                remoteDirectorySDF: false, 
                                removePrefix: '', 
                                sourceFiles: '**')], 
                            usePromotionTimestamp: false, 
                            useWorkspaceInPromotion: false, 
                            verbose: true
                            )
                        ]
                    )
                }
            }
            post{
                cleanup{
                    cleanWs deleteDirs: true, patterns: [
                        [pattern: 'source', type: 'INCLUDE'],
                        [pattern: 'build*', type: 'INCLUDE'],
                        ]
                }
            }
        }
    }
}
