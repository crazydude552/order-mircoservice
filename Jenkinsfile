pipeline {
    agent any

    environment {
        DOCKER_USER   = 'pvmrmoorthy'
        IMAGE_NAME    = 'order-microservice'
        OPENSHIFT_URL = 'https://api.rm3.7wse.p1.openshiftapps.com:6443'
        OS_PROJECT    = 'pvmrmoorthy-dev'
        APP_PORT      = '9000'
    }

    stages {
        stage('Build & Push Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin

                        docker build -t ${DOCKER_USER}/${IMAGE_NAME}:latest .
                        docker push ${DOCKER_USER}/${IMAGE_NAME}:latest
                    '''
                }
            }
        }

        stage('Deploy to OpenShift Sandbox') {
            steps {
                withCredentials([string(credentialsId: 'openshift-token', variable: 'OS_TOKEN')]) {
                    sh '''
                        oc login --token=${OS_TOKEN} --server=${OPENSHIFT_URL}
                        oc project ${OS_PROJECT}

                        # Apply deployment with explicit non-root user and resource limits
                        oc create deployment ${IMAGE_NAME} --image=${DOCKER_USER}/${IMAGE_NAME}:latest --dry-run=client -o yaml | oc apply -f -

                        # Set low memory/CPU limits for sandbox quotas
                        oc set resources deployment/${IMAGE_NAME} --requests=cpu=100m,memory=128Mi --limits=cpu=500m,memory=256Mi

                        # Expose internal ClusterIP service on port 9000
                        oc create service clusterip ${IMAGE_NAME} --tcp=${APP_PORT}:${APP_PORT} --dry-run=client -o yaml | oc apply -f -

                        # Create Edge-terminated HTTPS route
                        oc create route edge ${IMAGE_NAME} --service=${IMAGE_NAME} --port=${APP_PORT} --dry-run=client -o yaml | oc apply -f -

                        # Restart pod to fetch fresh image from Docker Hub
                        oc rollout restart deployment/${IMAGE_NAME}
                        oc rollout status deployment/${IMAGE_NAME} --timeout=120s
                    '''
                }
            }
        }

        stage('Verify Public Endpoint') {
            steps {
                withCredentials([string(credentialsId: 'openshift-token', variable: 'OS_TOKEN')]) {
                    sh '''
                        oc login --token=${OS_TOKEN} --server=${OPENSHIFT_URL} > /dev/null 2>&1

                        # Extract the dynamic Sandbox HTTPS route URL
                        ROUTE_HOST=$(oc get route ${IMAGE_NAME} -n ${OS_PROJECT} -o jsonpath='{.spec.host}')
                        echo "Testing Sandbox endpoint: https://${ROUTE_HOST}/healthz"

                        # Test Liveness Endpoint
                        curl -s -k https://${ROUTE_HOST}/healthz | grep "ok"
                    '''
                }
            }
        }
    }
}