pipeline {
    agent { label 'iot' }

    environment {
        REPO_URL = 'https://github.com/Angad0691996/AWS-IoT-Vehicle-Telematics.git'
        GIT_BRANCH = 'angad'
        BASE_DIR = '/home/ubuntu'
        CLONE_DIR = "${BASE_DIR}/AWS-IoT-Vehicle-Telematics"
        SCRIPT_DIR = "${CLONE_DIR}/scripts"
        APP_DIR = "${CLONE_DIR}/subscriber"  // Updated to "subscriber"
        VENV_NAME = "myenv"
        DB_USER = "iot_user"
        DB_PASSWORD = "Mycloud@25"
        DB_HOST = "localhost"
        DB_NAME = "vehicle_data"
        SERVICE_NAME = "subscriber.service"
    }

    stages {
        stage('Clone Git Repo') {
            steps {
                sh """
                    set -e
                    cd "$BASE_DIR"
                    rm -rf AWS-IoT-Vehicle-Telematics
                    git clone -b $GIT_BRANCH $REPO_URL
                    ls "$APP_DIR"
                """
            }
        }

        stage('Create MySQL Table') {
            steps {
                sh """
                    mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < "$SCRIPT_DIR/create_table.sql"
                """
            }
        }

        stage('Set up Python Virtual Environment') {
            steps {
                sh """
                    sudo apt-get update
                    sudo apt-get install -y python3-venv

                    cd "$APP_DIR"
                    python3 -m venv $VENV_NAME

                    # Ensure proper permissions for virtual environment and scripts
                    sudo chmod -R 755 "$APP_DIR/$VENV_NAME"
                    sudo chmod +x "$APP_DIR/ec2_subscriber.py"

                    # Activate the virtual environment
                    . "$APP_DIR/$VENV_NAME/bin/activate"

                    # Now you can use 'python' and 'pip' directly as the virtual environment is activated
                    python -m pip install --upgrade pip
                    python -m pip install -r "$APP_DIR/requirements.txt"
                """
            }
        }

        stage('Create systemd Service') {
            steps {
                sh """
                    cat <<EOF | sudo tee /etc/systemd/system/$SERVICE_NAME
[Unit]
Description=IoT EC2 Subscriber Service
After=network.target mysql.service

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR
ExecStart=/bin/bash -c '. $APP_DIR/$VENV_NAME/bin/activate && python $APP_DIR/ec2_subscriber.py'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

                    # Reload and restart systemd to enable the new service
                    sudo systemctl daemon-reexec
                    sudo systemctl daemon-reload
                    sudo systemctl enable $SERVICE_NAME
                    sudo systemctl restart $SERVICE_NAME
                    sudo systemctl status $SERVICE_NAME --no-pager
                """
            }
        }
    }
}
