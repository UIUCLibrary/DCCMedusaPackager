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



pipeline {
    agent none
//     agent {
//         label "Windows && Python3"
//     }
    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time
//         timeout(60)  // Timeout after 60 minutes. This shouldn't take this long but it hangs for some reason
//         checkoutToSubdirectory("source")
        buildDiscarder logRotator(artifactDaysToKeepStr: '30', artifactNumToKeepStr: '30', daysToKeepStr: '100', numToKeepStr: '100')
    }
//     environment {
//         PATH = "${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
//     }
    triggers {
        cron('@daily')
    }
    parameters {
//         booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        string(name: "PROJECT_NAME", defaultValue: "Medusa Packager", description: "Name given to the project")
        booleanParam(name: "PACKAGE_CX_FREEZE", defaultValue: false, description: "Create a package with CX_Freeze")
        // todo: set DEPLOY_DEVPI to default false
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: true, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to https://devpi.library.illinois.edu/production/release")
        booleanParam(name: "DEPLOY_SCCM", defaultValue: false, description: "Request deployment of MSI installer to SCCM")
        booleanParam(name: "UPDATE_DOCS", defaultValue: false, description: "Update the documentation")
        string(name: 'URL_SUBFOLDER', defaultValue: "DCCMedusaPackager", description: 'The directory that the docs should be saved under')
    }

    stages {
        stage("Getting Distribution Info"){
               agent {
                    dockerfile {
                        filename 'CI/docker/python/linux/Dockerfile'
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
//         stage("Configure") {
//             stages{
//                 stage("Purge All Existing Data in Workspace"){
//                     when{
//                         anyOf{
//                             equals expected: true, actual: params.FRESH_WORKSPACE
//                             triggeredBy "TimerTriggerCause"
//                         }
//                     }
//                     steps {
//                         deleteDir()
//                         dir("source"){
//                             checkout scm
//                         }
//                     }
//                     post{
//                         success {
//                             bat "dir /s /B"
//                         }
//                     }
//                 }
//                 stage("Stashing Important files for Later"){
//                     steps{
//                         dir("source"){
//                             stash includes: 'deployment.yml', name: "Deployment"
//                         }
//                     }
//                 }
//                 stage("Getting Distribution Info"){
//                     environment{
//                         PATH = "${tool 'CPython-3.7'};$PATH"
//                     }
//                     steps{
//                         dir("source"){
//                             bat "python setup.py dist_info"
//                         }
//                     }
//                     post{
//                         success{
//                             dir("source"){
//                                 stash includes: "MedusaPackager.dist-info/**", name: 'DIST-INFO'
//                                 archiveArtifacts artifacts: "MedusaPackager.dist-info/**"
//                             }
//                         }
//                     }
//                 }
//                 stage("Creating Virtualenv for Building"){
//                     steps{
//                         bat "python -m venv venv"
//                         script {
//                             try {
//                                 bat "call venv\\Scripts\\python.exe -m pip install -U pip"
//                             }
//                             catch (exc) {
//                                 bat "${tool 'CPython-3.6'}\\python -m venv venv"
//                                 bat "call venv\\Scripts\\python.exe -m pip install -U pip --no-cache-dir"
//                             }
//                         }
//                         bat "venv\\Scripts\\pip.exe install -U setuptools"
//                         bat "venv\\Scripts\\pip.exe install pytest pytest-cov lxml flake8 sphinx==1.6.7 wheel -r source\\requirements.txt -r source\\requirements-dev.txt --upgrade-strategy only-if-needed"
//                         bat "venv\\Scripts\\pip.exe install \"tox>=3.7\""
//                     }
//                     post{
//                         success{
//                             bat "(if not exist logs mkdir logs) && venv\\Scripts\\pip.exe list > ${WORKSPACE}\\logs\\pippackages_venv_${NODE_NAME}.log"
//                             archiveArtifacts artifacts: "logs/pippackages_venv_${NODE_NAME}.log"
//                         }
//                     }
//                 }
//             }
//         }
        stage("Building") {
            stages{
                stage("Building Python Package"){
                    agent {
                        dockerfile {
                            filename 'CI/docker/python/linux/Dockerfile'
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
                            filename 'CI/docker/python/linux/Dockerfile'
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
//                         echo "Building docs on ${env.NODE_NAME}"
//                         dir("source"){
//                             powershell "& ${WORKSPACE}\\venv\\Scripts\\python.exe setup.py build_sphinx --build-dir ${WORKSPACE}\\build\\docs | tee ${WORKSPACE}\\logs\\build_sphinx.log"
//                         }
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
                            filename 'CI/docker/python/linux/Dockerfile'
                            label 'linux && docker'
                        }
                    }
                    steps{
                        sh "pyton -m pytest --junitxml=reports/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:reports/coverage/ --cov=MedusaPackager" //  --basetemp={envtmpdir}"
//                         bat "${WORKSPACE}\\venv\\Scripts\\pytest.exe --junitxml=${WORKSPACE}/reports/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:${WORKSPACE}/reports/coverage/ --cov=MedusaPackager" //  --basetemp={envtmpdir}"
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
                            filename 'CI/docker/python/linux/Dockerfile'
                            label 'linux && docker'
                        }
                    }
                    steps{
                        sh "mypy -p MedusaPackager --junit-xml=junit-${env.NODE_NAME}-mypy.xml --html-report reports/mypy_html"
//                         bat "${WORKSPACE}\\venv\\Scripts\\mypy.exe -p MedusaPackager --junit-xml=${WORKSPACE}/junit-${env.NODE_NAME}-mypy.xml --html-report ${WORKSPACE}/reports/mypy_html"
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
                            filename 'CI/docker/python/linux/Dockerfile'
                            label 'linux && docker'
                        }
                    }
                    steps{
                            sh "python -m sphinx -b doctest docs/source build/docs -d build/docs/doctrees -v -w logs/doctest.log --no-color"
//                         dir("source"){
//                             bat "${WORKSPACE}\\venv\\Scripts\\sphinx-build.exe -b doctest docs\\source ${WORKSPACE}\\build\\docs -d ${WORKSPACE}\\build\\docs\\doctrees -v -w ${WORKSPACE}/logs/doctest.log --no-color"
//                         }
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
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\scripts\\python.exe setup.py sdist --format zip -d ${WORKSPACE}\\dist bdist_wheel -d ${WORKSPACE}\\dist"
                        }
                        
                    }
                    post{
                        success{
                                archiveArtifacts artifacts: "dist/*.whl,dist/*.tar.gz,dist/*.zip", fingerprint: true
                                stash includes: "dist/*.whl,dist/*.tar.gz,dist/*.zip", name: 'PYTHON_PACKAGES'
//                            }
                        }
                    }
                }
                stage("Windows CX_Freeze MSI"){
                    when{
                        anyOf{
                            equals expected: true, actual: params.PACKAGE_CX_FREEZE
                            triggeredBy "TimerTriggerCause"
                        }
                    }
                    environment {
                        PATH = "${WORKSPACE}\\venv\\Scripts;${tool 'CPython-3.6'};$PATH"
                    }
                    steps{
                        bat "venv\\Scripts\\pip.exe install -r source\\requirements.txt -r source\\requirements-dev.txt -r source\\requirements-freeze.txt"
                        dir("source"){
                            bat "python cx_setup.py bdist_msi --add-to-path=true -k --bdist-dir ../build/msi -d ${WORKSPACE}\\dist"
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

        stage("Deploy to Devpi"){
            when {
                allOf{
                    anyOf{
                        equals expected: true, actual: params.DEPLOY_DEVPI
                        triggeredBy "TimerTriggerCause"
                    }
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                    }
                }
            }
            options{
                timestamps()
                }
            environment{
                PATH = "${WORKSPACE}\\venv\\Scripts;${tool 'CPython-3.6'};${tool 'CPython-3.6'}\\Scripts;${PATH}"
                PKG_NAME = get_package_name("DIST-INFO", "MedusaPackager.dist-info/METADATA")
                PKG_VERSION = get_package_version("DIST-INFO", "MedusaPackager.dist-info/METADATA")
                DEVPI = credentials("DS_devpi")
            }
            stages{
                stage("Installing DevPi Client"){
                    steps{
                        bat "pip install devpi-client"
                    }
                }
                stage("Uploading to Package to DevPi Staging") {


                    steps {
                        unstash 'DOCS_ARCHIVE'
                        unstash 'PYTHON_PACKAGES'

                        bat "devpi use https://devpi.library.illinois.edu && devpi login ${env.DEVPI_USR} --password ${env.DEVPI_PSW} && devpi use /${env.DEVPI_USR}/${env.BRANCH_NAME}_staging && devpi upload --from-dir dist"
                    }
                }
                stage("Test DevPi Packages") {
                    parallel {
                        stage("Testing DevPi .zip Package with Python 3.6"){
                            environment {
                                PATH = "${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
                            }
                            agent {
                                node {
                                    label "Windows && Python3"
                                }
                            }
                            options {
                                skipDefaultCheckout(true)

                            }
                            stages{
                                stage("Creating venv to Test sdist"){
                                        steps {
                                            lock("system_python_${NODE_NAME}"){
                                                bat "python -m venv venv\\venv36"
                                            }
                                            bat 'venv\\venv36\\Scripts\\python.exe -m pip install pip --upgrade && venv\\venv36\\Scripts\\pip.exe install setuptools --upgrade && venv\\venv36\\Scripts\\pip.exe install "tox<3.7" devpi-client'
                                        }

                                }
                                stage("Testing DevPi zip Package"){

                                    environment {
                                        PATH = "${WORKSPACE}\\venv\\venv36\\Scripts;${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
                                    }
                                    steps {
                                        echo "Testing Source zip package in devpi"

                                        timeout(10){
                                            devpiTest(
                                                devpiExecutable: "${powershell(script: '(Get-Command devpi).path', returnStdout: true).trim()}",
                                                url: "https://devpi.library.illinois.edu",
                                                index: "${env.BRANCH_NAME}_staging",
                                                pkgName: "${env.PKG_NAME}",
                                                pkgVersion: "${env.PKG_VERSION}",
                                                pkgRegex: "zip",
                                                detox: false
                                            )
                                        }
                                    }
                                }
                            }
                            post {
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        disableDeferredWipeout: true,
                                        patterns: [
                                            [pattern: 'source', type: 'INCLUDE'],
                                            [pattern: '*tmp', type: 'INCLUDE'],
                                            [pattern: 'certs', type: 'INCLUDE']
                                            ]
                                    )
                                }
                            }

                        }
                        stage("Testing DevPi .whl Package with Python 3.6"){
                            agent {
                                node {
                                    label "Windows && Python3"
                                }
                            }

                            options {
                                skipDefaultCheckout(true)
                            }
                            stages{
                                stage("Creating venv to Test py36 .whl"){
                                    environment {
                                        PATH = "${tool 'CPython-3.6'};$PATH"
                                    }
                                    steps {
                                        lock("system_python_${NODE_NAME}"){
                                            bat "(if not exist venv\\36 mkdir venv\\36) && python -m venv venv\\36"
                                        }
                                        bat "venv\\36\\Scripts\\python.exe -m pip install pip --upgrade && venv\\36\\Scripts\\pip.exe install setuptools --upgrade && venv\\36\\Scripts\\pip.exe install \"tox<3.7\" devpi-client"
                                    }

                                }
                                stage("Testing DevPi .whl Package with Python 3.6"){
                                    options{
                                        timeout(10)
                                    }
                                    environment {
                                        PATH = "${WORKSPACE}\\venv\\36\\Scripts;$PATH"
                                    }

                                    steps {

                                        devpiTest(
                                                devpiExecutable: "${powershell(script: '(Get-Command devpi).path', returnStdout: true).trim()}",
                                                url: "https://devpi.library.illinois.edu",
                                                index: "${env.BRANCH_NAME}_staging",
                                                pkgName: "${env.PKG_NAME}",
                                                pkgVersion: "${env.PKG_VERSION}",
                                                pkgRegex: "whl",
                                                detox: false,
                                                toxEnvironment: "py36"
                                            )

                                    }
                                }
                            }
                            post {
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        disableDeferredWipeout: true,
                                        patterns: [
                                            [pattern: 'source', type: 'INCLUDE'],
                                            [pattern: '*tmp', type: 'INCLUDE'],
                                            [pattern: 'certs', type: 'INCLUDE']
                                            ]
                                    )
                                }
                            }
                        }
                    }

                }
                stage("Release to DevPi Production") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                            branch "master"
                        }
                    }
                    steps {
                        script {
                            try{
                                timeout(30) {
                                    input "Release ${env.pkg_name} ${PKG_VERSION} (https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging/${env.pkg_name}/${PKG_VERSION}) to DevPi Production? "
                                }
                                bat "venv\\Scripts\\devpi.exe login ${env.DEVPI_USR} --password ${env.DEVPI_PSW}"

                                bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                                bat "venv\\Scripts\\devpi.exe push ${env.pkg_name}==${env.PKG_VERSION} production/release"
                            } catch(err){
                                echo "User response timed out. Packages not deployed to DevPi Production."
                            }
                        }
                    }
                }
            }
            post {
                success {
                    echo "pushing to ${env.BRANCH_NAME}_staging"
                    bat "devpi use https://devpi.library.illinois.edu/${env.BRANCH_NAME}_staging"
                    bat "devpi login ${env.DEVPI_USR} --password ${env.DEVPI_PSW} && venv\\Scripts\\devpi.exe use http://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging && venv\\Scripts\\devpi.exe push ${env.PKG_NAME}==${env.PKG_VERSION} DS_Jenkins/${env.BRANCH_NAME}"
                }
                cleanup{
                    remove_from_devpi("venv\\Scripts\\devpi.exe", "${env.PKG_NAME}", "${env.PKG_VERSION}", "/${env.DEVPI_USR}/${env.BRANCH_NAME}_staging", "${env.DEVPI_USR}", "${env.DEVPI_PSW}")
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
    post{
        cleanup{
            cleanWs deleteDirs: true, patterns: [
                    [pattern: 'source', type: 'INCLUDE'],
                    [pattern: 'certs', type: 'INCLUDE'],
                    [pattern: 'build*', type: 'INCLUDE'],
                    [pattern: '*tmp', type: 'INCLUDE'],
                    [pattern: 'dist*', type: 'INCLUDE'],
                    [pattern: 'logs*', type: 'INCLUDE'],
                    [pattern: 'reports*', type: 'INCLUDE']
                    ]
        }
    }
}
