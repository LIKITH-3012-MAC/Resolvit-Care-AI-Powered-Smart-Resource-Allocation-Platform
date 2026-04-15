# Smart Resource Allocation

**AI-Powered Social Impact Operating System**
Built by **Likith Naidu Anumakonda**

> Transform scattered community data into coordinated action. Match the right volunteers and resources to the right needs at the right time.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Frontend (HTML/CSS/JS)              │
│  Landing · Auth · Dashboard · Map · Cases · Report  │
├────────────────────┬────────────────────────────────┤
│  FastAPI (8000)    │  Auth Service (3000)            │
│  Reports API       │  JWT + OTP + Resend Email      │
│  Volunteers API    │  Password Reset                │
│  Tasks API         │  Token Rotation                │
│  Analytics API     │                                │
│  Maps API          │                                │
├────────────────────┴────────────────────────────────┤
│              AI/ML Layer (Python)                    │
│  NLP Classifier · Priority Scorer · Matcher          │
│  Geospatial Clustering · Explainable AI              │
├─────────────────────────────────────────────────────┤
│              PostgreSQL + Redis                      │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Resend API Key (optional, for email)

### 2. Setup

```bash
# Clone and enter project
cd -p

# Copy env and configure
cp .env.example .env
# Edit .env with your values

# Start infrastructure
docker compose up -d

# Initialize database
docker exec -i smart_resource_db psql -U postgres -d smart_resource < database/schema.sql
docker exec -i smart_resource_db psql -U postgres -d smart_resource < database/seed.sql
```

### 3. Install Dependencies

```bash
# Python backend
pip install -r requirements.txt

# Auth service
cd auth && npm install && cd ..
```

### 4. Run Services

```bash
# Terminal 1 — FastAPI backend
uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — Auth service
cd auth && npm run dev

# Visit: http://127.0.0.1:8000
```

## Project Structure

```
├── ai/                    # AI/ML modules
│   ├── __init__.py         # NLP text classifier
│   ├── priority.py         # Priority scoring engine
│   ├── matcher.py          # Volunteer-task matching
│   ├── clustering.py       # Geospatial clustering
│   └── explainer.py        # Explainable AI module
├── auth/                  # Node.js auth service
│   └── src/
│       ├── controllers/    # Auth controller
│       ├── services/       # OTP, token, password, email
│       ├── middleware/      # JWT middleware
│       └── utils/           # Validators
├── backend/               # FastAPI backend
│   ├── app.py              # Main application
│   ├── config.py           # Environment config
│   ├── database.py         # Async PostgreSQL pool
│   ├── models.py           # Pydantic schemas
│   └── routes/             # API routes
├── database/              # SQL files
│   ├── schema.sql          # Full schema (12 tables)
│   └── seed.sql            # Demo data
├── frontend/              # Static frontend
│   ├── css/                # Design system + components
│   ├── js/                 # API client + theme
│   └── *.html              # Pages
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Pages

| Page | URL | Description |
|------|-----|-------------|
| Landing | `/` | Hero + features + CTA |
| Sign Up | `/signup.html` | 3-step OTP signup flow |
| Sign In | `/login.html` | Email/password login |
| Forgot Password | `/forgot-password.html` | Reset link request |
| Reset Password | `/reset-password.html` | Token-based reset |
| Dashboard | `/dashboard.html` | KPIs, reports, volunteers |
| Live Map | `/map.html` | Leaflet with 4 layers |
| Cases | `/cases.html` | Filterable case manager |
| Submit Report | `/report.html` | AI-classified submission |
| Analytics | `/analytics.html` | Impact metrics + charts |

## AI Features

- **NLP Classifier**: Categorizes reports into 10+ categories
- **Priority Scorer**: 8-factor weighted urgency scoring with fairness boosts
- **Volunteer Matcher**: 7-factor intelligent matching algorithm
- **Hotspot Detection**: K-means++ and DBSCAN geospatial clustering
- **Explainable AI**: Human-readable justifications for all decisions

## API Documentation

Visit `http://127.0.0.1:8000/docs` for interactive Swagger UI.

## Demo Credentials

- **Admin**: `admin@smartresource.org` / `Admin@123456`

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3 (Glassmorphism), Vanilla JS |
| Map | Leaflet.js + CARTO dark tiles |
| Backend API | FastAPI + asyncpg |
| Auth | Express.js + JWT + Resend |
| Database | PostgreSQL 16 |
| Cache | Redis |
| AI/ML | Python NLP + scoring engines |

---

*© 2026 Smart Resource Allocation. All rights reserved.*
# HACKATHON-VIT-AP
# Resolvit-Care-AI-Powered-Smart-Resource-Allocation-Platform
