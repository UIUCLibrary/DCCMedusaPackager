#!groovy
@Library("ds-utils")
import org.ds.*

def PKG_NAME = "unknown"
def PKG_VERSION = "unknown"
def DOC_ZIP_FILENAME = "doc.zip"
def junit_filename = "junit.xml"
def REPORT_DIR = ""
def VENV_ROOT = ""
def VENV_PYTHON = ""
def VENV_PIP = ""

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
                        equals expected: true, actual: params.FRESH_WORKSPACE
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
                            bat "dir /s"
                        }
                    }
                }
                stage("stashing inportant files for later"){
                    steps{
                        dir("source"){
                            stash includes: '**', name: "Source"
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
                    }
                }
                stage("Creating virtualenv for building"){
                    steps{
                        bat "${tool 'CPython-3.6'} -m venv venv"
                        script {
                            try {
                                bat "call venv\\Scripts\\python.exe -m pip install -U pip"
                            }
                            catch (exc) {
                                bat "${tool 'CPython-3.6'} -m venv venv"
                                bat "call venv\\Scripts\\python.exe -m pip install -U pip --no-cache-dir"
                            }                           
                        }    
                        bat "venv\\Scripts\\pip.exe install devpi-client --upgrade-strategy only-if-needed"
                        bat "venv\\Scripts\\pip.exe install tox mypy lxml pytest flake8 --upgrade-strategy only-if-needed"
                        
                        tee("logs/pippackages_venv_${NODE_NAME}.log") {
                            bat "venv\\Scripts\\pip.exe list"
                        }
                    }
                    post{
                        always{
                            dir("logs"){
                                script{
                                    def log_files = findFiles glob: '**/pippackages_venv_*.log'
                                    log_files.each { log_file ->
                                        echo "Found ${log_file}"
                                        archiveArtifacts artifacts: "${log_file}"
                                        bat "del ${log_file}"
                                    }
                                }
                            }
                        }
                        failure {
                            deleteDir()
                        }
                    }
                }
                stage("Setting variables used by the rest of the build"){
                    steps{
                        
                        script {
                            // Set up the reports directory variable 
                            REPORT_DIR = "${pwd tmp: true}\\reports"
                           dir("source"){
                                PKG_NAME = bat(returnStdout: true, script: "@${tool 'CPython-3.6'}  setup.py --name").trim()
                                PKG_VERSION = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                           }
                        }

                        script{
                            DOC_ZIP_FILENAME = "${PKG_NAME}-${PKG_VERSION}.doc.zip"
                            junit_filename = "junit-${env.NODE_NAME}-${env.GIT_COMMIT.substring(0,7)}-pytest.xml"
                        }


                        
                        
                        script{
                            VENV_ROOT = "${WORKSPACE}\\venv\\"

                            VENV_PYTHON = "${WORKSPACE}\\venv\\Scripts\\python.exe"
                            bat "${VENV_PYTHON} --version"

                            VENV_PIP = "${WORKSPACE}\\venv\\Scripts\\pip.exe"
                            bat "${VENV_PIP} --version"
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
Report Directory                = ${REPORT_DIR}
documentation zip file          = ${DOC_ZIP_FILENAME}
Python virtual environment path = ${VENV_ROOT}
VirtualEnv Python executable    = ${VENV_PYTHON}
VirtualEnv Pip executable       = ${VENV_PIP}
junit_filename                  = ${junit_filename}
"""           

                }
                
            }
        }
        stage("Unit tests") {
            when {
                expression { params.UNIT_TESTS == true }
            }
            parallel {
                stage("PyTest"){
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
            }
        }
        stage("Additional tests") {
            when {
                expression { params.ADDITIONAL_TESTS == true }
            }
            parallel{
                stage("MyPy"){
                    // agent{
                    //     node {
                    //         label "Windows && Python3"
                    //     }
                    // }
                    steps{
                        // bat "${tool 'CPython-3.6'} -m venv venv"
//                            bat "call make.bat install-dev"
                        // bat "venv\\Scripts\\pip.exe install mypy lxml"
                        dir("source") {
                            bat "${WORKSPACE}\\venv\\Scripts\\mypy.exe -p MedusaPackager --junit-xml=${WORKSPACE}/junit-${env.NODE_NAME}-mypy.xml --html-report ${WORKSPACE}/reports/mypy_html"
                        }
                        
                        // bat "${tool 'CPython-3.6'} -m mypy -p MedusaPackager --junit-xml=junit-${env.NODE_NAME}-mypy.xml --html-report reports/mypy_html"

                    }
                    post{
                        always {
                            junit "junit-${env.NODE_NAME}-mypy.xml"
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy_html', reportFiles: 'index.html', reportName: 'MyPy', reportTitles: ''])
                        }
                    }
                }
                stage("Documentation"){
                    // agent{
                    //     node {
                    //         label "Windows && Python3"
                    //     }
                    // }
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\Scripts\\sphinx-build.exe -b doctest docs\\source ${WORKSPACE}\\build\\docs -d ${WORKSPACE}\\build\\docs\\doctrees -v" 
                        }
                        
                        // bat "${tool 'CPython-3.6'} -m venv venv"
                        // bat "venv\\Scripts\\pip.exe install tox"
                        // bat "venv\\Scripts\\tox.exe -e docs"
                    }

                }
            }
        }
        stage("Packaging") {
            when {
                expression { params.DEPLOY_DEVPI == true || params.RELEASE != "None"}
            }
            // steps {
            parallel {
                stage("Source and Wheel formats"){
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\scripts\\python.exe setup.py sdist -d ${WORKSPACE}\\dist bdist_wheel -d ${WORKSPACE}\\dist"
                        }
                        
                        // bat """call ${WORKSPACE}\\venv\\Scripts\\activate.bat
                        //        pip install -r requirements.txt
                        //        pip install -r requirements-dev.txt
                        //        python setup.py sdist bdist_wheel
                        //         """

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
                    steps{
                            // deleteDir()
                            // checkout scm
                        bat "${tool 'CPython-3.6'} -m venv venv"
                        bat "make freeze"

                    }
                    post{
                        success{
                            dir("dist") {
                                stash includes: "*.msi", name: "msi"
                                archiveArtifacts artifacts: "*.msi", fingerprint: true
                            }
                        }
                    }
                }
                // parallel(
                    // "Source and Wheel formats": {
                    //     bat """${tool 'CPython-3.6'} -m venv venv
                    //             call venv\\Scripts\\activate.bat
                    //             pip install -r requirements.txt
                    //             pip install -r requirements-dev.txt
                    //             python setup.py sdist bdist_wheel
                    //             """
                    //     dir("dist"){
                    //         archiveArtifacts artifacts: "*.whl", fingerprint: true
                    //         archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
                    //     }
                    // },
                    // "Windows CX_Freeze MSI": {
                    //     node(label: "Windows") {
                    //         deleteDir()
                    //         checkout scm
                    //         bat "${tool 'CPython-3.6'} -m venv venv"
                    //         bat "make freeze"
                    //         dir("dist") {
                    //             stash includes: "*.msi", name: "msi"
                    //             archiveArtifacts artifacts: "*.msi", fingerprint: true
                    //         }

                    //     }
                    //     node(label: "Windows") {
                    //         deleteDir()
                    //         git url: 'https://github.com/UIUCLibrary/ValidateMSI.git'
                    //         unstash "msi"
                    //         bat "call validate.bat -i"
                            
                    //     }
                    // },
                    //     "Source Package": {
                    //         createSourceRelease(env.PYTHON3, "Source")
                    //     },
                    //     "Python Wheel:": {
                    //         node(label: "Windows") {
                    //             deleteDir()
                    //             unstash "Source"
                    //             withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                    //                 bat """
                    //   ${env.PYTHON3} -m venv .env
                    //   call .env/Scripts/activate.bat
                    //   pip install -r requirements.txt
                    //   python setup.py bdist_wheel
                    // """
                    //                 dir("dist") {
                    //                     archiveArtifacts artifacts: "*.whl", fingerprint: true
                    //                 }
                    //             }
                    //         }
                    //     },
                        // "Python CX_Freeze Windows": {
                        //     node(label: "Windows") {
                        //         deleteDir()
                        //         unstash "Source"
                        //         withEnv(["PATH=${env.PYTHON3}/..:${env.PATH}"]) {
                        //             bat """
                        //                 ${env.PYTHON3} cx_setup.py bdist_msi --add-to-path=true
                        //                 """
                        //             dir("dist") {
                        //                 archiveArtifacts artifacts: "*.msi", fingerprint: true
                        //                 stash includes: "*.msi", name: "msi"
                        //             }
                        //         }
                        //     }
                        // }
                // )
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
            // when {
            //     expression { params.DEPLOY_DEVPI == true }
            // }
            steps {
                bat "venv\\Scripts\\devpi.exe use http://devpy.library.illinois.edu"
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                    script {
                        bat "venv\\Scripts\\devpi.exe upload --from-dir dist"
                        try {
                            bat "venv\\Scripts\\devpi.exe upload --only-docs"
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
                        skipDefaultCheckout(true)
                    }
                    steps {
                        echo "Testing Whl package in devpi"
                        bat "${tool 'CPython-3.6'} -m venv venv"
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
            // parallel(
            //         "Source": {
            //             script {
            //                 def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
            //                 def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
            //                 node("Windows") {
            //                     withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
            //                         bat "${tool 'CPython-3.6'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
            //                         bat "${tool 'CPython-3.6'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
            //                         echo "Testing Source package in devpi"
            //                         script {
            //                              def devpi_test = bat(returnStdout: true, script: "${tool 'CPython-3.6'} -m devpi test --index http://devpy.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name} -s tar.gz").trim()
            //                              if(devpi_test =~ 'tox command failed') {
            //                                 error("Tox command failed")
            //                             }
            //                         }
            //                     }
            //                 }

            //             }
            //         },
            //         "Wheel": {
            //             script {
            //                 def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
            //                 def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
            //                 node("Windows") {
            //                     withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
            //                         bat "${tool 'CPython-3.6'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
            //                         bat "${tool 'CPython-3.6'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
            //                         echo "Testing Whl package in devpi"
            //                         script {
            //                             def devpi_test =  bat(returnStdout: true, script: "${tool 'CPython-3.6'} -m devpi test --index http://devpy.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name} -s whl").trim()
            //                             if(devpi_test =~ 'tox command failed') {
            //                                 error("Tox command failed")
            //                             }

            //                         }

            //                     }
            //                 }

            //             }
            //         }
            // )

//            }
            post {
                success {
                    echo "it Worked. Pushing file to ${env.BRANCH_NAME} index"
                    script {
                        def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                        def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            bat "venv\\Scripts\\devpi.exe push ${name}==${version} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
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
                    def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                    def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                    input("Are you sure you want to push ${name} version ${version} to production? This version cannot be overwritten.")
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "${tool 'CPython-3.6'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        bat "${tool 'CPython-3.6'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                        bat "${tool 'CPython-3.6'} -m devpi push ${name}==${version} production/release"
                    }

                }
                node("Linux"){
                    updateOnlineDocs url_subdomain: params.URL_SUBFOLDER, stash_name: "HTML Documentation"
                }
            }
        }
        stage("Update online documentation") {
            agent any
            when {
                expression { params.UPDATE_DOCS == true }
            }
            steps {
                updateOnlineDocs stash_name: "HTML Documentation", url_subdomain: params.URL_SUBFOLDER
            }
        }
    }
    post{
        cleanup{
            script {
                if (env.BRANCH_NAME == "master" || env.BRANCH_NAME == "dev"){
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "venv\\Scripts\\devpi.exe login DS_Jenkins --password ${DEVPI_PASSWORD}"
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                    }

                    def devpi_remove_return_code = bat returnStatus: true, script:"venv\\Scripts\\devpi.exe remove -y ${PKG_NAME}==${PKG_VERSION}"
                    echo "Devpi remove exited with code ${devpi_remove_return_code}."
                }
            }
            bat "dir"
        }
    }
}
