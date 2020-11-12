#!groovy
@Library("ds-utils")
import org.ds.*

@Library(["devpi", "PythonHelpers"]) _

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

def CONFIGURATIONS = [
    "3.6": [
            package_testing: [
                whl: [
                    pkgRegex: "*.whl",
                ],
                sdist: [
                    pkgRegex: "*.zip",
                ]
            ],
            test_docker_image: "python:3.6-windowsservercore",
            tox_env: "py36",
            devpi_wheel_regex: "cp36"

        ],
    "3.7": [
            package_testing: [
                whl: [
                    pkgRegex: "*.whl",
                ],
                sdist:[
                    pkgRegex: "*.zip",
                ]
            ],
            test_docker_image: "python:3.7",
            tox_env: "py37",
            devpi_wheel_regex: "cp37"
        ],
    "3.8": [
            package_testing: [
                whl: [
                    pkgRegex: "*.whl",
                ],
                sdist:[
                    pkgRegex: "*.zip",
                ]
            ],
            test_docker_image: "python:3.8",
            tox_env: "py38",
            devpi_wheel_regex: "cp38"
        ]
]
def tox

node(){
    checkout scm
    tox = load("ci/jenkins/scripts/tox.groovy")
}

pipeline {
    agent none
    parameters {
        string(name: "PROJECT_NAME", defaultValue: "Medusa Packager", description: "Name given to the project")
        booleanParam(name: "PACKAGE_CX_FREEZE", defaultValue: false, description: "Create a package with CX_Freeze")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: false, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to https://devpi.library.illinois.edu/production/release")
        booleanParam(name: "DEPLOY_SCCM", defaultValue: false, description: "Request deployment of MSI installer to SCCM")
        booleanParam(name: "UPDATE_DOCS", defaultValue: false, description: "Update the documentation")
        string(name: 'URL_SUBFOLDER', defaultValue: "DCCMedusaPackager", description: 'The directory that the docs should be saved under')
    }

    stages {
        stage("Run Tox"){
//             when{
//                 equals expected: true, actual: params.TEST_RUN_TOX
//             }
            steps {
                script{
                    def windowsJobs
                    def linuxJobs
                    stage("Scanning Tox Environments"){
                        parallel(
                            "Linux":{
                                linuxJobs = tox.getToxTestsParallel("Tox Linux", "linux && docker", "ci/docker/python/linux/tox/Dockerfile", "--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL")
                            },
//                             "Windows":{
//                                 windowsJobs = tox.getToxTestsParallel("Tox Windows", "windows && docker", "ci/docker/python/windows/tox/Dockerfile", "--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE")
//                             },
                            failFast: true
                        )
                    }
                    parallel(linuxJobs)
//                     parallel(windowsJobs + linuxJobs)
                }
            }
        }
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
        stage("Tests") {

            parallel {
                stage("PyTest"){
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker'
                        }
                    }
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
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker'
                        }
                    }
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
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker'
                        }
                    }
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
                        sh "python setup.py sdist --format zip -d dist bdist_wheel -d dist"
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
                    }
                }
                beforeAgent true
            }
            options{
                timestamps()
                lock("MedusaPackager-devpi")
            }
            environment{
                DEVPI = credentials("DS_devpi")
            }
            stages{
                stage("Deploy to Devpi Staging") {
                    agent {
                        dockerfile {
                            filename 'ci/docker/deploy/devpi/deploy/Dockerfile'
                            label 'linux&&docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                          }
                    }
                    steps {
                        unstash 'DOCS_ARCHIVE'
                        unstash 'PYTHON_PACKAGES'
                        sh(
                                label: "Connecting to DevPi Server",
                                script: 'devpi use https://devpi.library.illinois.edu --clientdir ${WORKSPACE}/devpi && devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ${WORKSPACE}/devpi'
                            )
                        sh(
                            label: "Uploading to DevPi Staging",
                            script: """devpi use /${env.DEVPI_USR}/${env.BRANCH_NAME}_staging --clientdir ${WORKSPACE}/devpi
devpi upload --from-dir dist --clientdir ${WORKSPACE}/devpi"""
                        )
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
                stage("Test DevPi packages") {
                    matrix {
                        axes {
                            axis {
                                name 'FORMAT'
                                values 'zip', "whl"
                            }
                            axis {
                                name 'PYTHON_VERSION'
                                values '3.6', "3.7", "3.8"
                            }
                        }
                        agent {
                          dockerfile {
                            additionalBuildArgs "--build-arg PYTHON_DOCKER_IMAGE_BASE=${CONFIGURATIONS[PYTHON_VERSION].test_docker_image}"
                            filename 'ci/docker/deploy/devpi/test/windows/Dockerfile'
                            label 'windows && docker'
                          }
                        }
                        stages{
                            stage("Testing DevPi Package"){
                                steps{
                                    script{
                                        timeout(10){
                                            unstash "DIST-INFO"
                                            def props = readProperties interpolate: true, file: 'MedusaPackager.dist-info/METADATA'
                                            bat(
                                                label: "Connecting to Devpi Server",
                                                script: "devpi use https://devpi.library.illinois.edu --clientdir certs\\ && devpi login %DEVPI_USR% --password %DEVPI_PSW% --clientdir certs\\ && devpi use ${env.BRANCH_NAME}_staging --clientdir certs\\"
                                            )
                                            bat(
                                                label: "Testing ${FORMAT} package stored on DevPi with Python version ${PYTHON_VERSION}",
                                                script: "devpi test --index ${env.BRANCH_NAME}_staging ${props.Name}==${props.Version} -s ${FORMAT} --clientdir certs\\ -e ${CONFIGURATIONS[PYTHON_VERSION].tox_env} -v"
                                            )
                                        }
                                    }
                                }
                                post{
                                    cleanup{
                                        cleanWs(
                                            deleteDirs: true,
                                            patterns: [
                                                [pattern: "dist/", type: 'INCLUDE'],
                                                [pattern: "certs/", type: 'INCLUDE'],
                                                [pattern: "MedusaPackager.dist-info/", type: 'INCLUDE'],
                                                [pattern: 'build/', type: 'INCLUDE']
                                            ]
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
                stage("Deploy to DevPi Production") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                            branch "master"
                        }
                        beforeAgent true
                        beforeInput true
                    }
                    agent {
                        dockerfile {
                            filename 'ci/docker/deploy/devpi/deploy/Dockerfile'
                            label 'linux&&docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                          }
                    }
                    input {
                        message 'Release to DevPi Production?'
                    }
                    steps {
                        unstash "DIST-INFO"
                        script{
                            def props = readProperties interpolate: true, file: "speedwagon.dist-info/METADATA"
                            sh "devpi login ${env.DEVPI_USR} --password ${env.DEVPI_PSW} && devpi use /${env.DEVPI_USR}/${env.BRANCH_NAME} && devpi push ${props.Name}==${props.Version} production/release"
                        }
                    }
                    post{
                        success{
                            jiraComment body: "Version ${PKG_VERSION} was added to https://devpi.library.illinois.edu/production/release index.", issueKey: "${params.JIRA_ISSUE_VALUE}"
                        }
                    }
                }

            }
            post{
                success{
                    node('linux && docker') {
                       script{
                            docker.build("uiucpresconpackager:devpi",'-f ./ci/docker/deploy/devpi/deploy/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .').inside{
                                unstash "DIST-INFO"
                                def props = readProperties interpolate: true, file: 'MedusaPackager.dist-info/METADATA'
                                sh(
                                    label: "Connecting to DevPi Server",
                                    script: 'devpi use https://devpi.library.illinois.edu --clientdir ${WORKSPACE}/devpi && devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ${WORKSPACE}/devpi'
                                )
                                sh(
                                    label: "Selecting to DevPi index",
                                    script: "devpi use /DS_Jenkins/${env.BRANCH_NAME}_staging --clientdir ${WORKSPACE}/devpi"
                                )
                                sh(
                                    label: "Pushing package to DevPi index",
                                    script:  "devpi push ${props.Name}==${props.Version} DS_Jenkins/${env.BRANCH_NAME} --clientdir ${WORKSPACE}/devpi"
                                )
                            }
                       }
                    }
                }
                cleanup{
                    node('linux && docker') {
                       script{
                            docker.build("uiucpresconpackager:devpi",'-f ./ci/docker/deploy/devpi/deploy/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .').inside{
                                unstash "DIST-INFO"
                                def props = readProperties interpolate: true, file: 'MedusaPackager.dist-info/METADATA'
                                sh(
                                    label: "Connecting to DevPi Server",
                                    script: 'devpi use https://devpi.library.illinois.edu --clientdir ${WORKSPACE}/devpi && devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ${WORKSPACE}/devpi'
                                )
                                sh(
                                    label: "Selecting to DevPi index",
                                    script: "devpi use /DS_Jenkins/${env.BRANCH_NAME}_staging --clientdir ${WORKSPACE}/devpi"
                                )
                                sh(
                                    label: "Removing package to DevPi index",
                                    script: "devpi remove -y ${props.Name}==${props.Version} --clientdir ${WORKSPACE}/devpi"
                                )
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
