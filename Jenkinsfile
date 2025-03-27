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
                git(
                    branch: 'main',
                    credentialsId: 'github-credentials',
                    url: 'https://github.com/Angad0691996/AWS-IoT-Vehicle-Telematics.git'
                )
            }
        }

        stage('Setup EC2 Environment') {
            steps {
                sshagent([SSH_CREDENTIALS_ID]) {
                    sh '''
                    ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST <<EOF
                    echo "Updating EC2 and installing dependencies..."
                    sudo apt update && sudo apt upgrade -y
                    
                    # Install Docker if not installed
                    if ! command -v docker &> /dev/null; then
                        echo "Installing Docker..."
                        sudo apt install -y docker.io
                        sudo systemctl enable --now docker
                        sudo usermod -aG docker $EC2_USER
                    fi

                    # Install MySQL if not installed
                    if ! command -v mysql &> /dev/null; then
                        echo "Installing MySQL..."
                        sudo apt install -y mysql-server
                        sudo systemctl enable --now mysql
                    fi

                    # Install Python3 & Grafana if needed
                    sudo apt install -y python3 python3-pip python3-venv grafana
                    sudo systemctl enable --now grafana-server
                    EOF
                    '''
                }
            }
        }

        stage('Setup MySQL Database') {
            steps {
                sshagent([SSH_CREDENTIALS_ID]) {
                    withCredentials([
                        string(credentialsId: 'mysql-root-password', variable: 'MYSQL_ROOT_PASS'),
                        string(credentialsId: 'mysql-iot-user-password', variable: 'MYSQL_IOT_PASS')
                    ]) {
                        sh '''
                        ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST <<EOF
                        echo "Configuring MySQL..."
                        sudo mysql <<MYSQL_SCRIPT
                        CREATE DATABASE IF NOT EXISTS vehicle_data;
                        CREATE USER IF NOT EXISTS 'iot_user'@'%' IDENTIFIED BY '$MYSQL_IOT_PASS';
                        GRANT ALL PRIVILEGES ON vehicle_data.* TO 'iot_user'@'%';
                        FLUSH PRIVILEGES;
                        MYSQL_SCRIPT
                        EOF
                        '''
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                echo "Building Docker Image..."
                sudo docker build -t $DOCKER_IMAGE .
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withDockerRegistry([credentialsId: 'docker-hub-credentials', url: 'https://index.docker.io/v1/']) {
                    sh '''
                    echo "Tagging and Pushing Docker Image..."
                    sudo docker tag $DOCKER_IMAGE $DOCKER_IMAGE
                    sudo docker push $DOCKER_IMAGE
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent([SSH_CREDENTIALS_ID]) {
                    withCredentials([
                        string(credentialsId: 'mysql-root-password', variable: 'MYSQL_ROOT_PASS'),
                        string(credentialsId: 'mysql-iot-user-password', variable: 'MYSQL_IOT_PASS'),
                        string(credentialsId: 'grafana-admin-password', variable: 'GRAFANA_PASS')
                    ]) {
                        sh '''
                        ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST <<EOF
                        echo "Deploying Docker Container..."
                        sudo docker pull $DOCKER_IMAGE
                        sudo docker stop iot-subscriber || true
                        sudo docker rm iot-subscriber || true
                        sudo docker run -d -p 5000:5000 --name iot-subscriber \
                            -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASS \
                            -e MYSQL_IOT_USER_PASSWORD=$MYSQL_IOT_PASS \
                            -e GRAFANA_ADMIN_PASSWORD=$GRAFANA_PASS \
                            $DOCKER_IMAGE
                        EOF
                        '''
                    }
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                sshagent([SSH_CREDENTIALS_ID]) {
                    sh '''
                    echo "Verifying Deployment..."
                    ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST "sudo docker ps | grep iot-subscriber"
                    '''
                }
            }
        }
    }
}
