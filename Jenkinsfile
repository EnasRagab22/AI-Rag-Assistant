pipeline {
    agent any

    environment {
        REPO_URL           = 'https://github.com/EnasRagab22/AI-Rag-Assistant.git'
        BRANCH             = 'main'
        GIT_CREDENTIALS_ID = 'GitCred'
        SCANNER_HOME       = tool 'sonar-server'
        SonarContainer     = 'sonarqube'
        BACKEND_PORT       = '5050'
        FRONTEND_PORT      = '8522'
        SONAR_HOST         = 'sonarqube'      // container name — resolves inside Docker network
        SONAR_PORT         = '9000'
    }

    stages {

        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Checkout Code') {
            steps {
                git branch: "${env.BRANCH}",
                    credentialsId: "${env.GIT_CREDENTIALS_ID}",
                    url: "${env.REPO_URL}"
            }
        }

        stage('Down Containers') {
            steps {
                sh """
                    docker stop tips_hindawi_backend  || true
                    docker stop tips_hindawi_frontend || true
                    docker rm   tips_hindawi_backend  || true
                    docker rm   tips_hindawi_frontend || true
                """
            }
        }

        stage('Ensure SonarQube Running') {
            steps {
                sh """
                    if [ "\$(docker ps -q -f name=${SonarContainer})" ]; then
                        echo "SonarQube container (${SonarContainer}) is already running ✅"
                    else
                        if [ "\$(docker ps -aq -f name=${SonarContainer})" ]; then
                            echo "Container exists but stopped → starting..."
                            docker start ${SonarContainer}
                        else
                            echo "Container not found → creating..."
                            docker run -d \
                                --name ${SonarContainer} \
                                --network enterpriseaiassistant_tipshindawicompany_app_network \
                                -p 9000:9000 \
                                --restart=always \
                                -v sonar_data:/opt/sonarqube/data \
                                -v sonar_extensions:/opt/sonarqube/extensions \
                                sonarqube:lts
                        fi
                    fi

                    echo "⏳ Waiting for SonarQube to be ready..."
                    until curl -s http://${SONAR_HOST}:${SONAR_PORT}/api/system/status | grep -q '"status":"UP"'; do
                        echo "Waiting for SonarQube..."
                        sleep 5
                    done
                    echo "✅ SonarQube is ready"
                """
            }
        }

        stage('SonarQube Scan') {
            steps {
                script {
                    def projectName = env.JOB_NAME.replaceAll('/', '_')

                    withSonarQubeEnv('sonar-server') {
                        sh """
                            ${SCANNER_HOME}/bin/sonar-scanner \
                                -Dsonar.projectKey=${projectName} \
                                -Dsonar.projectName=${projectName} \
                                -Dsonar.sources=.
                        """
                    }
                }
            }
        }

        stage('Create .env') {
            steps {
                withCredentials([
                    string(credentialsId: 'HF_TOKEN', variable: 'HF_TOKEN'),
                    string(credentialsId: 'API_KEY',  variable: 'API_KEY')
                ]) {
                    sh '''
                        cat > .env <<EOF
HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}
API_KEY=${API_KEY}
DATA_DIR=/app/data
HF_HOME=/app/.cache/huggingface
EOF
                    '''
                }
            }
        }

        stage('Deploy Stack') {
            steps {
                sh '''
                    docker-compose up -d --build tips_hindawi_backend tips_hindawi_frontend
                '''
            }
        }

        stage('Post Check') {
            steps {
                sh """
                    docker ps
                    echo "⏳ Waiting for backend to load Llama 3 model..."
                    sleep 30

                    curl -f http://tips_hindawi_backend:8000/health || exit 1
                    echo "✅ Backend is up"

                    curl -f http://tips_hindawi_frontend:8501 || exit 1
                    echo "✅ Frontend is up"
                """
            }
        }
    }

    post {
        always {
            echo "Pipeline finished"
        }
        success {
            echo "Deployment successful ✅"
            echo "Frontend URL : http://localhost:${FRONTEND_PORT}"
            echo "Backend URL  : http://localhost:${BACKEND_PORT}"
            echo "SonarQube    : http://localhost:${SONAR_PORT}"
        }
        failure {
            echo "Deployment failed ❌"
            sh "docker logs tips_hindawi_backend --tail=50 || true"
        }
    }
}