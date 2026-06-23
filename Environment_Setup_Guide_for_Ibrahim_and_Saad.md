# Environment Setup Guide for Ibrahim & Saad

## What Each File Does

| File | Purpose | Who Needs It |
| --- | --- | --- |
| `backend/.env` | Backend configuration (MongoDB, Firebase Admin) | Ibrahim |
| `frontend/.env` | Frontend configuration (Firebase Web SDK, API URL) | Saad |
| `serviceAccountKey.json` | Firebase Admin SDK private key (NEVER share publicly!) | Ibrahim |
| `.env.example` | Template showing what values are needed (committed to Git) | Both (for reference) |

---

## Ibrahim (Backend Engineer)

### Create these files in `backend/` folder:

### File 1: `backend/.env`

**What it does:**
- Connects to MongoDB Atlas database
- Tells backend where to find Firebase Admin SDK key
- Sets CORS allowed origins

**Create file at:** `foreman-kanban/backend/.env`

**Copy this exact content:**

```env
# MongoDB Atlas Connection
MONGO_URI=mongodb+srv://foreman-admin:11223344@foreman-cluster.nrijqsu.mongodb.net/foreman_db?retryWrites=true&w=majority&appName=foreman-cluster

# Firebase Service Account Path
FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json

# Frontend URL for CORS
FRONTEND_URL=http://localhost:5173

# Environment
ENVIRONMENT=development
```

---

### File 2: `backend/serviceAccountKey.json`

**What it does:**
- Allows backend to verify Firebase ID tokens from frontend
- Grants backend admin access to Firebase project
- **⚠️ CRITICAL: Never commit this to Git!**

**Create file at:** `foreman-kanban/backend/serviceAccountKey.json`

**Content:** Ismail will send this to you separately via private DM.

> **DO NOT copy from this file — it's for reference only:**

```json
{
  "type": "service_account",
  "project_id": "foreman-kanban",
  "private_key_id": "xxxxxxxxxxxxxxxxxxxxxxx",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASC...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@foreman-kanban.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40foreman-kanban.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

---

### File 3: `backend/.env.example` (Reference Only)

**What it does:** Shows the format but with placeholder values (committed to Git for reference).

**Create file at:** `foreman-kanban/backend/.env.example`

```env
# MongoDB Atlas Connection
MONGO_URI=mongodb+srv://your-username:your-password@your-cluster.xxxxx.mongodb.net/foreman_db?retryWrites=true&w=majority

# Firebase Service Account Path
FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json

# Frontend URL for CORS
FRONTEND_URL=http://localhost:5173

# Environment
ENVIRONMENT=development
```

---

## Saad (Frontend Engineer)

### Create these files in `frontend/` folder:

### File 1: `frontend/.env`

**What it does:**
- Tells frontend where the backend API is
- Provides Firebase Web SDK configuration for authentication
- ALL variables must start with `VITE_` (Vite requirement)

**Create file at:** `foreman-kanban/frontend/.env`

**Copy this exact content:**

```env
# API URL (Backend address)
VITE_API_URL=http://localhost:8000

# Firebase Web App Configuration
VITE_FIREBASE_API_KEY=AIzaSyDuDfvIxAJQXvpRPf36--dN6OQpGhK9-QM
VITE_FIREBASE_AUTH_DOMAIN=foreman-kanban.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=foreman-kanban
VITE_FIREBASE_STORAGE_BUCKET=foreman-kanban.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=599549835519
VITE_FIREBASE_APP_ID=1:599549835519:web:c4d55483745ae1ec7e74ca
```

---

### File 2: `frontend/.env.example` (Reference Only)

**What it does:** Shows the format but with placeholder values (committed to Git for reference).

**Create file at:** `foreman-kanban/frontend/.env.example`

```env
# API URL
VITE_API_URL=http://localhost:8000

# Firebase Configuration
VITE_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef1234567890
```

---

## Folder Structure Summary

After setup, your folders should look like this:

```
foreman-kanban/
│
├── backend/
│   ├── .env                    ← Ibrahim: Copy content from above
│   ├── .env.example            ← Already in Git (reference only)
│   ├── serviceAccountKey.json  ← Ibrahim: Get from Ismail (private)
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── .env                    ← Saad: Copy content from above
│   ├── .env.example            ← Already in Git (reference only)
│   ├── src/
│   ├── package.json
│   └── Dockerfile
│
├── .gitignore                  ← Already has .env files listed
├── docker-compose.yml
└── README.md
```

---

## Important Rules

| Rule | Why |
| --- | --- |
| **NEVER commit `.env` files** | They contain passwords and secrets |
| **NEVER commit `serviceAccountKey.json`** | It's a private key — anyone with it can access your Firebase |
| **Always use `.env.example` as template** | Shows format without exposing secrets |
| **Share secrets SECURELY** | Use encrypted ZIP, private DM, never email or chat |

---

## How to Verify Everything Works

### For Ibrahim (Backend):

```bash
cd backend

# Check if .env exists
ls -la .env

# Check if serviceAccountKey.json exists
ls -la serviceAccountKey.json

# Test loading environment
python -c "from app.config import MONGO_URI; print('✅ MONGO_URI loaded')"

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
✔ Firebase Admin SDK initialized from file: ./serviceAccountKey.json
✔ Connected to MongoDB: foreman_db
INFO: Application startup complete.
```

### For Saad (Frontend):

```bash
cd frontend

# Check if .env exists
ls -la .env

# Test loading environment
node -e "console.log('✅ API Key:', process.env.VITE_FIREBASE_API_KEY ? 'loaded' : 'NOT SET')"

# Run frontend
npm run dev
```

**Expected:** Open `http://localhost:5173` — should see the Foreman auth screen with **"Clock In" / "New Hire"** tabs.

---

## What Ismail Needs to Share

| File | How to Share | To Whom |
| --- | --- | --- |
| `backend/serviceAccountKey.json` | Private DM / Encrypted ZIP | Ibrahim ONLY |
| `backend/.env` content | Private DM (copy-paste) | Ibrahim |
| `frontend/.env` content | Private DM (copy-paste) | Saad |

> **⚠️ DO NOT share these in:**
> - Public chat
> - Email
> - WhatsApp
> - Any public repository

---

## Quick Setup Commands

### Ibrahim:

```bash
# 1. Clone the repo
git clone https://github.com/ismailrzw/foreman-kanban.git
cd foreman-kanban/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (copy content from above)

# 5. Place serviceAccountKey.json in backend/ folder

# 6. Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Saad:

```bash
# 1. Clone the repo
git clone https://github.com/ismailrzw/foreman-kanban.git
cd foreman-kanban/frontend

# 2. Install dependencies
npm install

# 3. Create .env file (copy content from above)

# 4. Run
npm run dev
```

---

## What Each Value Does

### MongoDB URI (for Ibrahim):

```
mongodb+srv://foreman-admin:11223344@foreman-cluster.nrijqsu.mongodb.net/foreman_db?retryWrites=true&w=majority&appName=foreman-cluster
```

| Part | Meaning |
| --- | --- |
| `foreman-admin` | Database username |
| `11223344` | Database password |
| `foreman-cluster.nrijqsu.mongodb.net` | Cluster address |
| `foreman_db` | Database name |
| `retryWrites=true&w=majority` | Connection settings |

### Firebase API Key (for Saad):

```
AIzaSyDuDfvIxAJQXvpRPf36--dN6OQpGhK9-QM
```

- Tells Firebase which project to connect to
- Publicly safe in frontend code (but still keep in `.env`)

### Firebase Auth Domain (for Saad):

```
foreman-kanban.firebaseapp.com
```

- Where Firebase authentication happens

---

## Troubleshooting

| Problem | Solution |
| --- | --- |
| **MongoDB connection fails** | Check if IP is whitelisted in Atlas (add `0.0.0.0/0`) |
| **Firebase Admin SDK fails** | Check `serviceAccountKey.json` path and content |
| **CORS error in browser** | Check `FRONTEND_URL` matches frontend address |
| **Frontend can't connect to backend** | Check `VITE_API_URL` matches backend address |
| **API key invalid error** | Verify no typos in `.env` files |
