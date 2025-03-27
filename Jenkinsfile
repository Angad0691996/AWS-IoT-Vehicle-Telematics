pipeline {
    agent any

    environment {
        EC2_USER = 'ubuntu'
        EC2_HOST = '13.232.172.49'
        SSH_CREDENTIALS_ID = 'ec2-ssh-key'
        DOCKER_IMAGE = 'angad/iot-subscriber:latest'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/Angad0691996/AWS-IoT-Vehicle-Telematics.git'
            }
        }

        stage('Setup EC2 Environment') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    sh '''
                    ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST <<EOF
                    sudo apt update && sudo apt upgrade -y

                    # Ensure Docker is installed
                    if ! command -v docker &> /dev/null; then
                        sudo apt install -y docker.io
                        sudo systemctl enable docker
                        sudo systemctl start docker
                        sudo usermod -aG docker ubuntu
                    fi

                    # Install MySQL if not installed
                    if ! command -v mysql &> /dev/null; then
                        sudo apt install -y mysql-server
                        sudo systemctl enable mysql
                        sudo systemctl start mysql
                    fi

                    # Install Python
                    sudo apt install -y python3 python3-pip python3-venv

                    # Install Grafana if not installed
                    if ! command -v grafana-server &> /dev/null; then
                        sudo apt install -y apt-transport-https software-properties-common wget
                        wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
                        echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
                        sudo apt update && sudo apt install -y grafana
                        sudo systemctl enable grafana-server
                        sudo systemctl start grafana-server
                    fi
                    EOF
                    '''
                }
            }
        }

        stage('Setup MySQL Database') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    withCredentials([
                        string(credentialsId: 'mysql-root-password', variable: 'MYSQL_ROOT_PASS'),
                        string(credentialsId: 'mysql-iot-user-password', variable: 'MYSQL_IOT_PASS')
                    ]) {
                        sh '''
                        ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST <<EOF
                        sudo mysql -e "CREATE DATABASE IF NOT EXISTS vehicle_data;"
                        sudo mysql -e "CREATE USER IF NOT EXISTS 'iot_user'@'%' IDENTIFIED BY '$MYSQL_IOT_PASS';"
                        sudo mysql -e "GRANT ALL PRIVILEGES ON vehicle_data.* TO 'iot_user'@'%';"
                        sudo mysql -e "FLUSH PRIVILEGES;"
                        EOF
                        '''
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t iot-subscriber .'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withDockerRegistry([credentialsId: 'docker-hub-credentials', url: 'https://index.docker.io/v1/']) {
                    sh '''
                    docker tag iot-subscriber $DOCKER_IMAGE
                    docker push $DOCKER_IMAGE
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    withCredentials([
                        string(credentialsId: 'mysql-root-password', variable: 'MYSQL_ROOT_PASS'),
                        string(credentialsId: 'mysql-iot-user-password', variable: 'MYSQL_IOT_PASS'),
                        string(credentialsId: 'grafana-admin-password', variable: 'GRAFANA_PASS')
                    ]) {
                        sh '''
                        ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST <<EOF
                        export MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASS
                        export MYSQL_IOT_USER_PASSWORD=$MYSQL_IOT_PASS
                        export GRAFANA_ADMIN_PASSWORD=$GRAFANA_PASS

                        docker pull $DOCKER_IMAGE
                        docker stop iot-subscriber || true
                        docker rm iot-subscriber || true
                        docker run -d -p 5000:5000 --name iot-subscriber \
                            -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
                            -e MYSQL_IOT_USER_PASSWORD=$MYSQL_IOT_USER_PASSWORD \
                            -e GRAFANA_ADMIN_PASSWORD=$GRAFANA_ADMIN_PASSWORD \
                            $DOCKER_IMAGE
                        EOF
                        '''
                    }
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    sh '''
                    ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST "docker ps | grep iot-subscriber"
                    '''
                }
            }
        }
    }
}
