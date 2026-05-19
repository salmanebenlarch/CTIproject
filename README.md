# SecRadar Starter

MVP scaffold for a security analysis web app inspired by threat-intelligence dashboards and URL/file reputation tools.

## Included features
- VirusTotal-powered analysis for files, URLs, IPs, domains, and hashes
- Dashboard tab with real persisted stats, recent analyses, analyst shortcuts, and live charts
  - analyses over time (daily + weekly line chart)
  - verdict distribution (donut chart)
  - analyses by type (bar chart)
- News tab backed by a backend proxy to the Hacker News API
- Category-filtered news with backend caching and frontend auto-refresh every 5 minutes
- News thumbnails fetched via backend OG-image proxying with placeholder fallback
- HIBP / Pwned? tab backed by the Have I Been Pwned API v3
- Login modal in the navbar
- Change password flow for logged-in users
- Admin vs User roles
- Admin-only runtime controls:
  - runtime VirusTotal API key override
  - view all analyses
  - create, delete, and re-role users
  - inspect analysis history per user

## Persistence and auth
- Users are stored in PostgreSQL via SQLAlchemy.
- Passwords are hashed with bcrypt.
- Access tokens are JWT bearer tokens with expiration.
- The default admin and analyst accounts are seeded on first run.
- Every analysis result is stored so the dashboard reflects real usage over time.
- Detailed detection stats are stored for each analysis so dashboard charts can use real persisted data.

## Run locally

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Create the database once if needed, for example: createdb secradar
uvicorn app.main:app --reload
```

With a running PostgreSQL database matching `DATABASE_URL`, this will create the app tables automatically on first start, create the new chart-support table, and seed the default users.

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Demo credentials
These come from `.env` and are seeded on first run if the users do not already exist:
- Admin: `admin / change-this-admin-password`
- User: `analyst / change-this-user-password`

## Frontend environment
Optional frontend environment variable:
- `VITE_API_BASE=http://localhost:8000/api`

## Notes
- The logout endpoint revokes the current JWT token instead of clearing an in-memory session.
- User deletion preserves old analysis records by keeping their historical username snapshot.
- News categories are heuristic keyword filters over Hacker News stories.
- HIBP requests are proxied through the backend because authenticated HIBP endpoints should not be called directly from the browser.
- Add `HIBP_API_KEY` to `.env` before using the Pwned? tab.

## Environment
See `.env.example`.
# CTIproject
# CTIproject
