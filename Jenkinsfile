#!groovy
@Library("ds-utils")
import org.ds.*

pipeline {
    agent {
        label "Windows"
    }
    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time
        timeout(60)  // Timeout after 60 minutes. This shouldn't take this long but it hangs for some reason
        // checkoutToSubdirectory("source")
    }
    environment {
        mypy_args = "--junit-xml=mypy.xml"
        // pytest_args = "--junitxml=reports/junit-{env:OS:UNKNOWN_OS}-{envname}.xml --junit-prefix={env:OS:UNKNOWN_OS}  --basetemp={envtmpdir}"
    }
    parameters {
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
                stage("Cloning Source") {
                    agent any
                    steps {
                        deleteDir()
                        echo "Cloning source"
                        checkout scm
                        stash includes: '**', name: "Source"
                        stash includes: 'deployment.yml', name: "Deployment"

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
                        bat "venv\\Scripts\\pip.exe install tox mypy pytest flake8--upgrade-strategy only-if-needed"
                    }
                }
            }
        }
        stage("Unit tests") {
            when {
                expression { params.UNIT_TESTS == true }
            }
            // steps {
                parallel {
                    stage("PyTest"){
                        steps{
                            bat "venv\\Scripts\\tox.exe -e pytest -- --junitxml=reports/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:reports/coverage/ --cov=MedusaPackager" //  --basetemp={envtmpdir}" 
                            junit "reports/junit-${env.NODE_NAME}-pytest.xml"
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/coverage', reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                        }
                    }
                }
                //     "PyTest": {
                //         // node(label: "Windows") {
                //             // checkout scm
                //             // bat "venv\\Scripts\\tox.exe -e pytest -- --junitxml=reports/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:reports/coverage/ --cov=MedusaPackager" //  --basetemp={envtmpdir}" 
                //             // junit "reports/junit-${env.NODE_NAME}-pytest.xml"
                //             // publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/coverage', reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                //          }
                //     }
                // )
                
            // }
        }
        // stage("Unit tests") {
        //     when {
        //         expression { params.UNIT_TESTS == true }
        //     }
        //     steps {
        //         parallel(
        //             "Windows": {
        //                 node(label: "Windows") {
        //                     script {
        //                         checkout scm
        //                         try {
        //                             bat "${tool 'CPython-3.6'} -m tox -e pytest -- --junitxml=reports/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest" 
        //                         } catch (exc) {
        //                             junit 'reports/junit-*.xml'
        //                             error("Unit test Failed on Windows")
        //                         }
        //                     }
        //                 }
        //             }
        //             // "Linux": {
        //             //     node(label: "Linux") {
        //             //         script {
        //             //             checkout scm
        //             //             try {
        //             //                 sh "${env.PYTHON3} -m tox"
        //             //             } catch (exc) {
        //             //                 junit 'reports/junit-*.xml'
        //             //                 error("Unit test Failed on Linux")
        //             //             }
        //             //         }
        //             //     }
        //             // }
        //         )
        //         // parallel(
        //         //         "Windows": {
        //         //             script {
        //         //                 def runner = new Tox(this)
        //         //                 runner.windows = true
        //         //                 runner.stash = "Source"
        //         //                 runner.label = "Windows"
        //         //                 runner.post = {
        //         //                     junit 'reports/junit-*.xml'
        //         //                 }
        //         //                 runner.run()
        //         //             }
        //         //         },
        //         //         "Linux": {
        //         //             script {
        //         //                 def runner = new Tox(this)
        //         //                 runner.windows = false
        //         //                 runner.stash = "Source"
        //         //                 runner.label = "!Windows"
        //         //                 runner.post = {
        //         //                     junit 'reports/junit-*.xml'
        //         //                 }
        //         //                 runner.run()
        //         //             }
        //         //         }
        //         // )
        //     }
        // }
        stage("Additional tests") {
            when {
                expression { params.ADDITIONAL_TESTS == true }
            }
            // steps {
                parallel{
                    stage("MyPy"){
                        agent{
                            node {
                                label "Windows && Python3"    
                            }
                        }
                        steps{
                            bat "call make.bat install-dev"
                            bat "venv\\Scripts\\mypy.exe -p MedusaPackager --junit-xml=junit-${env.NODE_NAME}-mypy.xml --html-report reports/mypy_html"
                            // bat "${tool 'CPython-3.6'} -m mypy -p MedusaPackager --junit-xml=junit-${env.NODE_NAME}-mypy.xml --html-report reports/mypy_html"
                            junit "junit-${env.NODE_NAME}-mypy.xml"
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy_html', reportFiles: 'index.html', reportName: 'MyPy', reportTitles: ''])
                        }
                    }
                    stage("Documentation"){
                        steps{
                            bat "venv\\Scripts\\tox.exe -e docs"
                        }

                    }
                }
                    // "MyPy": {
                     
                    //     node(label: "Windows") {
                    //         checkout scm
                    //         bat "call make.bat install-dev"
                    //         bat "venv\\Scripts\\mypy.exe -p MedusaPackager --junit-xml=junit-${env.NODE_NAME}-mypy.xml --html-report reports/mypy_html"
                    //         // bat "${tool 'CPython-3.6'} -m mypy -p MedusaPackager --junit-xml=junit-${env.NODE_NAME}-mypy.xml --html-report reports/mypy_html"
                    //         junit "junit-${env.NODE_NAME}-mypy.xml"
                    //         publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy_html', reportFiles: 'index.html', reportName: 'MyPy', reportTitles: ''])
                    //      }
                    // },
                        //     script {
                        //         def runner = new Tox(this)
                        //         runner.env = "mypy"
                        //         runner.windows = true
                        //         runner.stash = "Source"
                        //         runner.label = "Windows"
                        //         runner.post = {
                        //             junit 'mypy.xml'
                        //         }
                        //         runner.run()

                        //     }
                        // },
                        // "Documentation": {
                        //     bat "${tool 'CPython-3.6'} -m tox -e docs"
                        //     // script {
                        //     //     def runner = new Tox(this)
                        //     //     runner.env = "docs"
                        //     //     runner.windows = true
                        //     //     runner.stash = "Source"
                        //     //     runner.label = "Windows"
                        //     //     runner.post = {
                        //     //         dir('.tox/dist/html/') {
                        //     //             stash includes: '**', name: "HTML Documentation", useDefaultExcludes: false
                        //     //         }
                        //     //     }
                        //     //     runner.run()

                        //     // }
                        // }
                // )
            // }
        }

        stage("Packaging") {
            when {
                expression { params.DEPLOY_DEVPI == true || params.RELEASE != "None"}
            }
            // steps {
            parallel {
                stage("Source and Wheel formats"){
                    steps{
                        bat """${tool 'CPython-3.6'} -m venv venv
                                call venv\\Scripts\\activate.bat
                                pip install -r requirements.txt
                                pip install -r requirements-dev.txt
                                python setup.py sdist bdist_wheel
                                """
                        dir("dist"){
                            archiveArtifacts artifacts: "*.whl", fingerprint: true
                            archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
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
                        dir("dist") {
                            stash includes: "*.msi", name: "msi"
                            archiveArtifacts artifacts: "*.msi", fingerprint: true
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
                expression { params.DEPLOY_DEVPI == true }
            }
//            steps {
            parallel {
                stage("Source Distribution: .tar.gz") {
                    environment {
                        PATH = "${tool 'CMake_3.11.4'}\\;$PATH"
                    }
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
                    environment {
                        PATH = "${tool 'CMake_3.11.4'}\\;$PATH"
                    }
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
                            bat "${tool 'CPython-3.6'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            bat "${tool 'CPython-3.6'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            bat "${tool 'CPython-3.6'} -m devpi push ${name}==${version} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
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
}
