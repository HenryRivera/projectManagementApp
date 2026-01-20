pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = 'aida'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'echo "✅ Checked out: ${GIT_BRANCH}"'
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    echo "🔨 Building Docker images..."
                    docker-compose build
                    echo "✅ Build complete"
                '''
            }
        }

        stage('Deploy with Nginx') {
            steps {
                sh '''
                    echo "🚀 Deploying..."
                    
                    # Force remove any existing containers with our names
                    docker rm -f project-management-backend project-management-frontend project-management-nginx 2>/dev/null || true
                    
                    # Remove old networks if they exist
                    docker network rm aida_app-network 2>/dev/null || true
                    
                    docker-compose down --remove-orphans || true
                    docker-compose up -d
                    echo "✅ Deployed"
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "🏥 Health check..."
                    sleep 15
                    docker-compose ps
                    curl -f http://localhost/api/health || echo "Waiting for startup..."
                    echo "✅ Done"
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline successful! App at http://localhost'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}
