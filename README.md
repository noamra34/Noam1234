# Supermarket Application

This project is a supermarket application deployed using Kubernetes and managed with Helm. The application consists of multiple namespaces, each serving a distinct purpose, including application deployment, CI/CD, continuous deployment, and monitoring.

## Project Structure

### Namespaces

1. **Default**
   - **MongoDB Pod**: Deployed using Helm.
   - **Flask Application Pods**: Three pods running the supermarket application.

2. **Jenkins**
   - **Jenkins Pod**: Deployed using Helm.
   - **Multibranch Pipeline**: Defined for feature and main branches. When a push to the Git repository (`Noam1234`) occurs on the feature branch, the pipeline builds an image and performs a merge request to the main branch. Upon approval, the pipeline runs on the main branch, builds an image, changes the tag version, pushes it to Docker Hub, updates the `Chart.yaml` version in the HelmChart, and pushes the changes to the main branch, avoiding an endless loop.

3. **ArgoCD**
   - **ArgoCD Pods**: Deployed using Helm.
   - **Continuous Deployment**: Monitors the GitHub repository and triggers a restart of the application pods when a new image is pushed to Docker Hub.

4. **Monitoring**
   - **Prometheus and Grafana Pods**: Deployed using Helm.
   - **Monitoring**: Tracks the CPU usage and other metrics for all namespaces.

## Setup Instructions

### Helm Installation and Upgrade

1. **Install the Helm Chart:**
   ```sh
   helm install mypj-release ./final-pj1
   ```
2. **Upgrade the Helm Chart:**
    ```sh
    helm upgrade mypj-release ./final-pj1 --values ./final-pj1/values.yaml
    ```
### Accessing Dashboards:
1. **Grafana Dashbord:**
    ```sh
    kubectl -n monitoring port-forward svc/my-prometheus-stack-grafana 3000:80
    ```
2. **Jenkins Dashbord:**
    ```sh
    kubectl -n jenkins port-forward svc/jenkins 8080:8080
    ```
3. **ArgoCD Dashbord:**
    ```sh
    kubectl -n argocd port-forward svc/argocd-server 8081:443
    ```
    username: admin
    password: adminpassword
4. **Prometheus Dashbord:**
    ```sh
    kubectl -n monitoring port-forward svc/prometheus-operated 9090:9090
    ```
5. **Flask Application:**
    ```sh
    kubectl get pods
    kubectl port-forward <flask-app-XXXXXXXXXX-XXXXX> 5000:5000


## Continuous Integration and Deployment
### Jenkins Pipeline
- **Feature Branch**: When a push is made to the feature branch, the pipeline builds an image and   performs a merge request to the main branch.

- **Main Branch**: After approving the merge request, the pipeline builds an image, updates the image tag version, pushes the image to Docker Hub, updates the Chart.yaml in HelmChart, and pushes the changes back to the main branch.

### ArgoCD
- Monitors the GitHub repository for changes.
- Automatically restarts application pods upon new image pushes to Docker Hub.

### Monitoring
- Prometheus and Grafana are set up to monitor the CPU and other metrics across all namespaces.

### Repository:
- GitHub Repository: ```https://github.com/noamra34/Noam1234```