# Setup & Installation Guide

> **Foreman Kanban** — Detailed setup instructions for local development, containerized environments, and cloud deployment.

---

## 1. Prerequisites

Before installing Foreman Kanban, ensure your system has the following software installed:

| Tool | Recommended Version | Purpose |
|------|--------------------|---------|
| **Node.js** | v20.x or higher | Frontend build tooling & dev server |
| **npm** | v10.x or higher | Frontend package manager |
| **Python** | v3.12.x | Backend runtime environment |
| **Docker** | v24.x or higher | Containerization engine |
| **Docker Compose** | v2.20.x or higher | Multi-container local orchestration |
| **kubectl** | v1.28.x or higher *(Optional)* | Kubernetes CLI |
| **minikube** | v1.32.x or higher *(Optional)* | Local Kubernetes cluster runner |

---

## 2. Environment Variables Configuration

Foreman Kanban relies on environment variables for API endpoints, database connections, and Firebase authentication credentials.

### 2.1 Backend Environment Variables (`backend/.env`)

Copy `backend/.env.example` to `backend/.env`:

```env
# MongoDB Atlas Connection
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/foreman_db?retryWrites=true&w=majority

# Firebase Service Account Path (Local File)
FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json

# OR Firebase Service Account JSON String (Cloud Environments)
# FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}

# Allowed Frontend Origins (CORS)
FRONTEND_URL=http://localhost:5173

# Application Environment (development | production | test)
ENVIRONMENT=development
```

### 2.2 Frontend Environment Variables (`frontend/.env`)

Copy `frontend/.env.example` to `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
VITE_FIREBASE_AUTH_DOMAIN=foreman-kanban.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=foreman-kanban
VITE_FIREBASE_STORAGE_BUCKET=foreman-kanban.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=1234567890
VITE_FIREBASE_APP_ID=1:1234567890:web:abcdef123456
```

---

## 3. Local Development Setup (Manual)

### 3.1 Backend Setup (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # macOS / Linux:
   python3 -m venv venv
   source venv/bin/activate

   # Windows (PowerShell):
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
5. Verify health check at `http://localhost:8000/api/health`.

### 3.2 Frontend Setup (React + Vite)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Access the application in your browser at `http://localhost:5173`.

---

## 4. Docker Compose Setup (Containerized)

To spin up the complete full-stack environment (`MongoDB`, `FastAPI Backend`, and `Nginx Frontend`) with a single command:

1. Copy the root environment file:
   ```bash
   cp .env.example .env
   ```
2. Launch containers in attached mode:
   ```bash
   docker-compose up --build
   ```
3. Access points:
   - **Frontend SPA:** `http://localhost:80`
   - **Backend API:** `http://localhost:8000`
   - **MongoDB Service:** `localhost:27017`

---

## 5. Kubernetes Setup (minikube)

To deploy Foreman Kanban to a local Kubernetes cluster:

1. Start minikube:
   ```bash
   minikube start
   ```
2. Enable ingress addon:
   ```bash
   minikube addons enable ingress
   ```
3. Apply all manifests in order:
   ```bash
   kubectl apply -f k8s/namespace.yml
   kubectl apply -f k8s/configmap.yml
   kubectl apply -f k8s/secrets.yml
   kubectl apply -f k8s/mongo-pv.yml
   kubectl apply -f k8s/mongo-deployment.yml
   kubectl apply -f k8s/backend-deployment.yml
   kubectl apply -f k8s/frontend-deployment.yml
   kubectl apply -f k8s/ingress.yml
   kubectl apply -f k8s/hpa.yml
   ```
4. Check pod status:
   ```bash
   kubectl get pods -n foreman
   ```
