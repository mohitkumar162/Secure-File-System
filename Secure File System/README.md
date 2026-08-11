# Secure File Management System

A secure, Dockerized Web Application built with Flask, integrated with AWS S3, and deployed using Kubernetes. It encrypts files on upload using AES-256 encryption and decrypts them on download. Authentication is secured using BCrypt passwords and Google Authenticator 2-Factor Authentication (2FA).

## 🚀 Key Features

*   **🔒 Secure Local/AWS S3 Storage**: Uploaded files are encrypted using 256-bit AES encryption. If AWS credentials are provided, files are stored securely in an Amazon S3 bucket.
*   **🔑 2-Factor Authentication (2FA)**: Login requires a password and a dynamic Google Authenticator TOTP token.
*   **🐳 Docker Containerization**: The app is containerized for consistent running on any platform.
*   **☸️ Kubernetes Orchestration**: Manifests are provided for deploying scalable replicas, load balancer services, and ingress traffic routing.
*   **🤖 GitHub Actions CI/CD**: Automatic testing (using pytest) and Docker image build verification on every code change.
*   **🐧 Linux Shell Scripting**: A simplified bash script (`deploy.sh`) to build and deploy everything on Linux.

---

## 🛠️ Technology Stack

*   **Backend**: Python, Flask, PyCryptodome (AES), PyOTP (2FA), BCrypt, Boto3 (AWS S3)
*   **Testing**: Pytest
*   **DevOps & Infrastructure**: Docker, Docker Compose, Kubernetes (YAML), GitHub Actions (YAML), AWS (S3, EKS, ECR, IAM, VPC), Linux (Bash Scripting)

---

## 🐳 Running with Docker

### Method 1: Using docker-compose (Recommended)
Build and run the entire environment with a single command:
```bash
docker-compose up --build
```
Open `http://localhost:5000` in your web browser.

### Method 2: Running manual Docker commands
1. Build the Docker image:
   ```bash
   docker build -t secure-file-system:latest "./Secure File Management System"
   ```
2. Run the Docker container:
   ```bash
   docker run -p 5000:5000 --name secure-file-system-app secure-file-system:latest
   ```

---

## ☸️ Running with Kubernetes

Deploy the application to a Kubernetes cluster (e.g., Minikube or AWS EKS):

1. **Apply Secrets**:
   Update `k8s/secrets.yaml` with your custom keys or AWS S3 credentials, then apply:
   ```bash
   kubectl apply -f k8s/secrets.yaml
   ```
2. **Deploy the App**:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```
3. **Expose the App**:
   ```bash
   kubectl apply -f k8s/service.yaml
   ```
4. **Deploy Ingress (Optional)**:
   ```bash
   kubectl apply -f k8s/ingress.yaml
   ```

---

## ☁️ AWS Deployment Architecture

This project is fully designed to deploy on **Amazon Web Services (AWS)**. The step-by-step visual configuration guides are saved in the `AWS Deployment/` folder:

1.  **VPC & Networking** (`AWS1.png`): Set up a public and private subnet architecture to securely isolate backend servers.
2.  **IAM Security Roles** (`AWS2.png`): Create IAM policies giving read/write S3 access to backend servers.
3.  **Amazon S3 Storage** (`AWS3.png`): Configure S3 Bucket settings (private access, server-side encryption).
4.  **Amazon ECR Registry** (`AWS4.png`): Build and push the Docker image to Amazon Elastic Container Registry (ECR).
5.  **Amazon EKS Cluster** (`AWS5.png`): Create an Elastic Kubernetes Service (EKS) cluster to host deployment replicas.
6.  **Load Balancer Integration** (`AWS6.png`): Map Kubernetes service routing to an AWS Application Load Balancer (ALB) to expose the app to users.

---

## 🤖 GitHub Actions CI/CD Pipeline

The `.github/workflows/ci-cd.yml` configuration runs automatically on every code change to check that:
1. Python dependencies install correctly.
2. All unit tests in the test suite pass (`pytest`).
3. The Docker container builds successfully.

---

## 🐧 Linux Deployment Script

For Linux systems, run the custom automation script to build the image and apply Kubernetes configurations:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 📝 Credentials for Local Testing

When starting the application, the terminal/Docker logs will output the active credentials:
*   **Username**: `admin`
*   **Password**: `admin123` (Configurable via `ADMIN_PASSWORD` environment variable)
*   **TOTP Secret**: A new secret is generated at startup and prints to console. Scan the printed QR code with Google Authenticator or enter the manual secret code to get the 2FA verify tokens.
