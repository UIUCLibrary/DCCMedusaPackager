#!groovy
@Library("ds-utils")
import org.ds.*

def PKG_NAME = "unknown"
def PKG_VERSION = "unknown"
def DOC_ZIP_FILENAME = "doc.zip"
def junit_filename = "junit.xml"

pipeline {
    agent {
        label "Windows"
    }
    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time
        timeout(60)  // Timeout after 60 minutes. This shouldn't take this long but it hangs for some reason
        checkoutToSubdirectory("source")
    }
    environment {
        mypy_args = "--junit-xml=mypy.xml"
        // pytest_args = "--junitxml=reports/junit-{env:OS:UNKNOWN_OS}-{envname}.xml --junit-prefix={env:OS:UNKNOWN_OS}  --basetemp={envtmpdir}"
    }
    triggers {
        cron('@daily')
    }
    parameters {
        booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        string(name: "PROJECT_NAME", defaultValue: "Medusa Packager", description: "Name given to the project")
        booleanParam(name: "UNIT_TESTS", defaultValue: true, description: "Run Automated Unit Tests")
        booleanParam(name: "ADDITIONAL_TESTS", defaultValue: true, description: "Run additional tests")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: true, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        choice(choices: 'None\nRelease_to_devpi_only\nRelease_to_devpi_and_sccm\n', description: "Release the build to production. Only available in the Master branch", name: 'RELEASE')
        booleanParam(name: "UPDATE_DOCS", defaultValue: false, description: "Update the documentation")
        string(name: 'URL_SUBFOLDER', defaultValue: "DCCMedusaPackager", description: 'The directory that the docs should be saved under')
        // booleanParam(name: "PACKAGE", defaultValue: true, description: "Create a Packages")
        // booleanParam(name: "DEPLOY", defaultValue: false, description: "Deploy SCCM")
    }

    stages {
        stage("Configure") {
            stages{
                stage("Purge all existing data in workspace"){
                    when{
                        anyOf{
                            equals expected: true, actual: params.FRESH_WORKSPACE
                            triggeredBy "TimerTriggerCause"
                        }
                    }
                    steps {
                        deleteDir()
                        bat "dir"
                        echo "Cloning source"
                        dir("source"){
                            checkout scm
                        }
                    }
                    post{
                        success {
                            bat "dir /s /B"
                        }
                    }
                }
                stage("Stashing important files for later"){
                    steps{
                        dir("source"){
                            stash includes: 'deployment.yml', name: "Deployment"
                        }
                    }
                }
                stage("Cleanup extra dirs"){
                    steps{
                        dir("reports"){
                            deleteDir()
                            echo "Cleaned out reports directory"
                            bat "dir"
                        }
                        dir("dist"){
                            deleteDir()
                            echo "Cleaned out dist directory"
                            bat "dir"
                        }
                        dir("build"){
                            deleteDir()
                            echo "Cleaned out build directory"
                            bat "dir"
                        }
                        dir("logs"){
                            deleteDir()
                            echo "Cleaned out logs directory"
                            bat "dir"
                        }
                    }
                }
                stage("Creating virtualenv for building"){
                    steps{
                        bat "${tool 'CPython-3.6'}\\python -m venv venv"
                        script {
                            try {
                                bat "call venv\\Scripts\\python.exe -m pip install -U pip"
                            }
                            catch (exc) {
                                bat "${tool 'CPython-3.6'}\\python -m venv venv"
                                bat "call venv\\Scripts\\python.exe -m pip install -U pip --no-cache-dir"
                            }
                        }
                        bat "venv\\Scripts\\pip.exe install -U setuptools"
//                        TODO: when detox is fixed, just use the most recent version
                        bat "venv\\Scripts\\pip.exe install devpi-client pytest pytest-cov lxml flake8 sphinx wheel -r source\\requirements.txt -r source\\requirements-dev.txt -r source\\requirements-freeze.txt --upgrade-strategy only-if-needed"
                        bat "venv\\Scripts\\pip.exe install detox==0.13 tox==3.2.1"
                    }
                    post{
                        success{
                            bat "venv\\Scripts\\pip.exe list > ${WORKSPACE}\\logs\\pippackages_venv_${NODE_NAME}.log"
                            archiveArtifacts artifacts: "logs/pippackages_venv_${NODE_NAME}.log"
                        }
                    }
                }
                stage("Setting variables used by the rest of the build"){
                    steps{
                        
                        script {
                            // Set up the reports directory variable 
                           dir("source"){
                                PKG_NAME = bat(returnStdout: true, script: "@${tool 'CPython-3.6'}\\python  setup.py --name").trim()
                                PKG_VERSION = bat(returnStdout: true, script: "@${tool 'CPython-3.6'}\\python setup.py --version").trim()
                           }
                        }

                        script{
                            DOC_ZIP_FILENAME = "${PKG_NAME}-${PKG_VERSION}.doc.zip"
                            junit_filename = "junit-${env.NODE_NAME}-${env.GIT_COMMIT.substring(0,7)}-pytest.xml"
                        }


                        bat "venv\\Scripts\\devpi use https://devpi.library.illinois.edu"
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {    
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        }
                        bat "dir"
                    }
                }
            }
            post{
                always{
                    echo """Name                            = ${PKG_NAME}
Version                         = ${PKG_VERSION}
documentation zip file          = ${DOC_ZIP_FILENAME}
junit_filename                  = ${junit_filename}
"""           

                }
                
            }
        }
        stage("Building") {
            stages{
                stage("Building Python Package"){
                    steps {


                        dir("source"){
                            powershell "& ${WORKSPACE}\\venv\\Scripts\\python.exe setup.py build -b ${WORKSPACE}\\build  | tee ${WORKSPACE}\\logs\\build.log"
                        }

                    }
                    post{
                        always{
                            warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'logs/build.log']]
                            archiveArtifacts artifacts: "logs/build.log"
                        }
                        failure{
                            echo "Failed to build Python package"
                        }
                    }
                }
                stage("Building Sphinx Documentation"){
                    steps {
                        echo "Building docs on ${env.NODE_NAME}"
                        dir("source"){
                            powershell "& ${WORKSPACE}\\venv\\Scripts\\python.exe setup.py build_sphinx --build-dir ${WORKSPACE}\\build\\docs | tee ${WORKSPACE}\\logs\\build_sphinx.log"
                        }
                    }
                    post{
                        always {
                            warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'logs/build_sphinx.log']]
                            archiveArtifacts artifacts: 'logs/build_sphinx.log'
                        }
                        success{
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                            zip archive: true, dir: "build/docs/html", glob: '', zipFile: "dist/${DOC_ZIP_FILENAME}"
                            stash includes: 'build/docs/html/**', name: 'docs'
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
                    when {
                        equals expected: true, actual: params.UNIT_TESTS
                    }
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\Scripts\\pytest.exe --junitxml=${WORKSPACE}/reports/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:${WORKSPACE}/reports/coverage/ --cov=MedusaPackager" //  --basetemp={envtmpdir}"
                        }

                    }
                    post {
                        always{
                            junit "reports/junit-${env.NODE_NAME}-pytest.xml"
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/coverage', reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                        }
                    }
                }
                stage("MyPy"){
                    when{
                        equals expected: true, actual: params.ADDITIONAL_TESTS
                    }
                    steps{
                        dir("source") {
                            bat "${WORKSPACE}\\venv\\Scripts\\mypy.exe -p MedusaPackager --junit-xml=${WORKSPACE}/junit-${env.NODE_NAME}-mypy.xml --html-report ${WORKSPACE}/reports/mypy_html"
                        }
                    }
                    post{
                        always {
                            junit "junit-${env.NODE_NAME}-mypy.xml"
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy_html', reportFiles: 'index.html', reportName: 'MyPy', reportTitles: ''])
                        }
                    }
                }
                stage("Documentation"){
                    when{
                        equals expected: true, actual: params.ADDITIONAL_TESTS
                    }
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\Scripts\\sphinx-build.exe -b doctest docs\\source ${WORKSPACE}\\build\\docs -d ${WORKSPACE}\\build\\docs\\doctrees -v"
                        }
                    }

                }
            }
        }
//        stage("Additional tests") {
//
//            when {
//
//            }
//            parallel{
//
//            }
//        }

        stage("Packaging") {
            when {
                expression { params.DEPLOY_DEVPI == true || params.RELEASE != "None"}
            }
            parallel {
                stage("Source and Wheel formats"){
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\scripts\\python.exe setup.py sdist -d ${WORKSPACE}\\dist bdist_wheel -d ${WORKSPACE}\\dist"
                        }
                        
                    }
                    post{
                        success{
                            dir("dist"){
                                archiveArtifacts artifacts: "*.whl", fingerprint: true
                                archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
                            }
                        }
                    }
                }
                stage("Windows CX_Freeze MSI"){
                    agent{
                        node {
                            label "Windows"
                        }
                    }
                    options {
                        skipDefaultCheckout true
                    }
                    steps{
                        bat "dir"
                        deleteDir()
                        bat "dir"
                        checkout scm
                        bat "dir /s / B"
                        bat "${tool 'CPython-3.6'}\\python -m venv venv"
                        bat "make freeze"


                    }
                    post{
                        success{
                            dir("dist") {
                                stash includes: "*.msi", name: "msi"
                                archiveArtifacts artifacts: "*.msi", fingerprint: true
                            }
                        }
                        cleanup{
                            bat "dir"
                            deleteDir()
                            bat "dir"
                        }
                    }
                }
            }
        }

        stage("Deploying to Devpi") {
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                    }
                }
            }
            steps {
                bat "venv\\Scripts\\devpi.exe use http://devpy.library.illinois.edu"
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                    script {
                        bat "venv\\Scripts\\devpi.exe upload --from-dir dist"
                        try {
//                            bat "venv\\Scripts\\devpi.exe upload --only-docs"
                            bat "venv\\Scripts\\devpi.exe upload --only-docs ${WORKSPACE}\\dist\\${DOC_ZIP_FILENAME}"
                        } catch (exc) {
                            echo "Unable to upload to devpi with docs."
                        }
                    }
                }

            }
        }
        stage("Test Devpi packages") {
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                    }
                }
            }
//            steps {
            parallel {
                stage("Source Distribution: .tar.gz") {
                    steps {
                        echo "Testing Source tar.gz package in devpi"
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"

                        }
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"

                        script {
                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${PKG_NAME} -s tar.gz  --verbose"
                            if(devpi_test_return_code != 0){
                                error "Devpi exit code for tar.gz was ${devpi_test_return_code}"
                            }
                        }
                        echo "Finished testing Source Distribution: .tar.gz"
                    }
                    post {
                        failure {
                            echo "Tests for .tar.gz source on DevPi failed."
                        }
                    }

                }
                stage("Source Distribution: .zip") {
                    steps {
                        echo "Testing Source zip package in devpi"
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        }
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                        script {
                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${PKG_NAME} -s zip --verbose"
                            if(devpi_test_return_code != 0){
                                error "Devpi exit code for zip was ${devpi_test_return_code}"
                            }
                        }
                        echo "Finished testing Source Distribution: .zip"
                    }
                    post {
                        failure {
                            echo "Tests for .zip source on DevPi failed."
                        }
                    }
                }
                stage("Built Distribution: .whl") {
                    agent {
                        node {
                            label "Windows && Python3"
                        }
                    }
                    options {
                        skipDefaultCheckout()
                    }
                    steps {
                        echo "Testing Whl package in devpi"
                        bat "${tool 'CPython-3.6'}\\python -m venv venv"
                        bat "venv\\Scripts\\pip.exe install tox devpi-client"
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        }
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                        script{
                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${PKG_NAME} -s whl  --verbose"
                            if(devpi_test_return_code != 0){
                                error "Devpi exit code for whl was ${devpi_test_return_code}"
                            }
                        }
                        echo "Finished testing Built Distribution: .whl"
                    }
                    post {
                        failure {
                            echo "Tests for whl on DevPi failed."
                        }
                    }
                }
            }

            post {
                success {
                    echo "it Worked. Pushing file to ${env.BRANCH_NAME} index"
                    script {
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            bat "venv\\Scripts\\devpi.exe push ${PKG_NAME}==${PKG_VERSION} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                        }
                    }
                }
            }
        }
        // stage("Deploy - Staging") {
        //     agent any
        //     when {
        //         expression { params.DEPLOY == true && params.PACKAGE == true }
        //     }
        //     steps {
        //         deployStash("msi", "${env.SCCM_STAGING_FOLDER}/${params.PROJECT_NAME}/")
        //         input("Deploy to production?")
        //     }
        // }

        // stage("Deploy - SCCM upload") {
        //     agent any
        //     when {
        //         expression { params.DEPLOY == true && params.PACKAGE == true }
        //     }
        //     steps {
        //         deployStash("msi", "${env.SCCM_UPLOAD_FOLDER}")
        //     }
        //     post {
        //         success {
        //             script{
        //                 unstash "Source"
        //                 def  deployment_request = requestDeploy this, "deployment.yml"
        //                 echo deployment_request
        //                 writeFile file: "deployment_request.txt", text: deployment_request
        //                 archiveArtifacts artifacts: "deployment_request.txt"
        //             }

        //         }
        //     }
        // }
        stage("Deploy to SCCM") {
            when {
                expression { params.RELEASE == "Release_to_devpi_and_sccm"}
            }

            steps {
                node("Linux"){
                    unstash "msi"
                    deployStash("msi", "${env.SCCM_STAGING_FOLDER}/${params.PROJECT_NAME}/")
                    input("Push a SCCM release?")
                    deployStash("msi", "${env.SCCM_UPLOAD_FOLDER}")
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
        stage("Release to DevPi production") {
            when {
                expression { params.RELEASE != "None" && env.BRANCH_NAME == "master" }
            }
            steps {
                script {
                    try{
                        timeout(30) {
                            input "Release ${PKG_NAME} ${PKG_VERSION} (https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging/${PKG_NAME}/${PKG_VERSION}) to DevPi Production? "
                        }
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        }

                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                        bat "venv\\Scripts\\devpi.exe push ${PKG_NAME}==${PKG_VERSION} production/release"
                    } catch(err){
                        echo "User response timed out. Packages not deployed to DevPi Production."
                    }
                }
            }
        }
        stage("Update online documentation") {
            agent any
            when {
                expression { params.UPDATE_DOCS == true }
            }
            steps {
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
                // updateOnlineDocs stash_name: "HTML Documentation", url_subdomain: params.URL_SUBFOLDER
            }
        }
    }
    post{
        cleanup{

            script {
                if(fileExists('source/setup.py')){
                    dir("source"){
                        try{
                            retry(3) {
                                bat "${WORKSPACE}\\venv\\Scripts\\python.exe setup.py clean --all"
                            }
                        } catch (Exception ex) {
                            echo "Unable to successfully run clean. Purging source directory."
                            deleteDir()
                        }
                    }
                }
                bat "dir"
                if (env.BRANCH_NAME == "master" || env.BRANCH_NAME == "dev"){
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "venv\\Scripts\\devpi.exe login DS_Jenkins --password ${DEVPI_PASSWORD}"
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                    }

                    def devpi_remove_return_code = bat returnStatus: true, script:"venv\\Scripts\\devpi.exe remove -y ${PKG_NAME}==${PKG_VERSION}"
                    echo "Devpi remove exited with code ${devpi_remove_return_code}."
                }
            }
            cleanWs deleteDirs: true, patterns: [
                    [pattern: 'build*', type: 'INCLUDE'],
                    [pattern: 'dist*', type: 'INCLUDE'],
                    [pattern: 'logs*', type: 'INCLUDE'],
                    [pattern: 'reports*', type: 'INCLUDE']
                    ]
//            bat "dir /s / B"
        }
    }
}
