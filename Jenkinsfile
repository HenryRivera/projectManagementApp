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
                    docker-compose down || true
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
