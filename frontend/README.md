# Foreman Frontend — React 19 + Vite SPA

Single-Page Application for **Foreman Kanban**, styled using the custom industrial "Foreman" design system.

---

## Tech Stack & Architecture

- **Framework:** React 19 + Vite 8
- **Routing:** React Router DOM 7
- **HTTP Client:** Axios with automatic Firebase Bearer ID token injection interceptor (`src/utils/api.js`)
- **Authentication:** Firebase Auth JS SDK (`src/firebase.js`) + AuthContext (`src/contexts/AuthContext.jsx`)
- **Styling:** Custom Vanilla CSS design tokens (`src/index.css`)

---

## Folder Structure

```
frontend/src/
├── assets/
│   └── hero.png              # UI hero display image
├── components/
│   ├── AuthScreen.jsx        # Login ("Clock In") & Signup ("New Hire") tabs
│   ├── BoardColumn.jsx       # Kanban stage column renderer
│   ├── InspectionQueue.jsx   # Manager review queue panel ("PR Inbox")
│   ├── NewTaskModal.jsx      # Work order creation modal
│   ├── RejectPanel.jsx       # Reusable rejection feedback component
│   ├── TicketCard.jsx        # Paper ticket with stamp animations & pins
│   ├── Toast.jsx             # Notification toast provider & component
│   └── Topbar.jsx            # Sticky navigation bar & user badge
├── contexts/
│   └── AuthContext.jsx       # Firebase auth & backend role state provider
├── pages/
│   ├── EmployeeDashboard.jsx # Filtered board view for employees
│   └── ManagerDashboard.jsx  # Complete board + inspection queue for managers
├── utils/
│   └── api.js                # Pre-configured Axios instance
├── App.jsx                   # Root component & role-based routing
├── firebase.js               # Firebase Client SDK initialization
├── index.css                 # Global styles & Foreman design system tokens
└── main.jsx                  # React DOM entry point
```

---

## Development & Build Commands

```bash
# Install dependencies
npm install

# Start Vite HMR dev server (http://localhost:5173)
npm run dev

# Lint code
npm run lint

# Build production bundle (outputs to dist/)
npm run build

# Preview production build
npm run preview
```

---

## Docker Containerization

The frontend uses a multi-stage Dockerfile:
1. **Stage 1 (builder):** Node 20 environment compiles the static React bundle via `npm run build`.
2. **Stage 2 (production):** `nginx:1.25-alpine` serves the static assets with gzip compression, SPA routing fallbacks, and API proxy rules (`nginx.conf`).
