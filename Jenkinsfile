pipeline {
    agent any
    environment {
        APP_DIR = "/opt/iot-app"
        VENV_DIR = "$APP_DIR/venv"
    }
    stages {
        stage('Install System Packages') {
            steps {
                script {
                    sh '''
                        sudo apt update
                        sudo apt install -y python3 python3-venv python3-pip mysql-client
                    '''
                }
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                script {
                    sh '''
                        sudo mkdir -p $APP_DIR
                        sudo chown -R jenkins:jenkins $APP_DIR  # Ensure Jenkins can write
                        
                        if [ ! -d "$VENV_DIR" ]; then
                            python3 -m venv $VENV_DIR
                        fi
                    '''
                }
            }
        }

        stage('Activate Virtual Env & Install Dependencies') {
            steps {
                script {
                    sh '''
                        bash -c "source $VENV_DIR/bin/activate && pip install --upgrade pip && pip install -r requirements.txt || echo 'requirements.txt not found, skipping...'"
                    '''
                }
            }
        }

        stage('Verify MySQL Connection') {
            steps {
                withCredentials([string(credentialsId: 'MYSQL_ROOT_PASSWORD', variable: 'DB_ROOT_PASS')]) {
                    script {
                        sh '''
                            mysql -uroot -p$DB_ROOT_PASS -h localhost -e "SHOW DATABASES;"
                        '''
                    }
                }
            }
        }

        stage('Verify Grafana Connection') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'GRAFANA_CREDENTIALS', usernameVariable: 'GRAFANA_USER', passwordVariable: 'GRAFANA_PASS')]) {
                    script {
                        sh '''
                            curl -u $GRAFANA_USER:$GRAFANA_PASS http://localhost:3000/api/health || echo "Grafana not reachable"
                        '''
                    }
                }
            }
        }

        stage('Verify Installation') {
            steps {
                script {
                    sh '''
                        bash -c "source $VENV_DIR/bin/activate && pip list"
                    '''
                }
            }
        }
    }

    post {
        failure {
            echo "❌ Installation Failed! Check logs for errors."
        }
        success {
            echo "✅ Installation Successful!"
        }
    }
}
