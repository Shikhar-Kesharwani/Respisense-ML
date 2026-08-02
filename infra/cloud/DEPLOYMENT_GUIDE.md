# Model 1 — Cloud-Native Deployment Guide (Managed Services)

This architecture provides a zero-maintenance, production-ready managed deployment suitable for portfolio projects, recruiter demonstrations, and live public demos.

---

## Final Architecture Stack

```text
                 GitHub
                    │
             GitHub Actions
                    │
       ┌────────────┴────────────┐
       │                         │
       ▼                         ▼
    Frontend                 Backend
     Vercel              Google Cloud Run (or Render)
       │                         │
       └────────────┬────────────┘
                    │
                HTTPS API
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
  Neon Postgres   Cloudflare R2   Upstash Redis
                    │
                    ▼
                 Sentry
```

---

## 1. Component Specifications

### 1.1 Frontend
- **Preferred:** **Vercel** (Global CDN, automatic HTTPS, preview deployments, instant GitHub integration).
- **Fallback:** **Cloudflare Pages**.

### 1.2 Backend (API & ML Pipeline)
- **Standard API & Lightweight ML:** **Google Cloud Run** (Container-based, auto-scaling, scale-to-zero, free tier eligible).
- **Fallback:** **Render Web Service** (Free tier container hosting).
- **Heavy Resource ML:** If resource demands exceed Cloud Run free limits, deploy to **Oracle Cloud Always Free VM** (4 Arm Ampere A1 cores, 24GB RAM free forever) or Model 2 Docker stack.

### 1.3 Database Selection Engine
1. **Default Choice (Priority #1):** **Neon**
   - Native Serverless PostgreSQL with connection pooling and instant branching.
2. **Integrated Services Choice (Priority #2):** **Supabase**
   - Use when built-in Authentication, Storage, and Realtime capabilities are required.
3. **Enterprise Choice (Priority #3):** **CockroachDB**
   - Use for multi-region or distributed SQL demonstrations.

### 1.4 Object Storage (X-Rays & Artifacts)
- **Preferred:** **Cloudflare R2** (10GB Free Storage, $0 Egress Fees, S3-compatible API).
- **Fallback:** **Supabase Storage**.

### 1.5 Cache & Queue
- **Preferred:** **Upstash Redis** (Serverless Redis for sessions, caching, rate-limiting, and AI memory).
- **Fallback:** Self-hosted Redis container.

### 1.6 Authentication Engine
- **Simple Email Login:** Supabase Auth
- **Enterprise Login:** Clerk
- **Internal API Protection:** JWT (JSON Web Tokens)

### 1.7 Monitoring & Analytics
- **Error Tracking & Performance:** **Sentry** (Auto-tracks runtime exceptions, stack traces, and API performance).
- **Analytics:** **Vercel Analytics** or **PostHog**.

### 1.8 Health Checks
The backend application automatically exposes:
- `GET /health` -> Overall health status
- `GET /ready` -> Readiness probe
- `GET /live` -> Liveness probe

---

## 2. Step-by-Step Deployment Instructions

### Step 1: Deploy Backend to Google Cloud Run (or Render)
1. Push code to GitHub repository.
2. Connect repository to Google Cloud Run (or Render).
3. Set environment variables:
   - `PORT` = `8080`
   - `FLASK_ENV` = `production`
   - `DATABASE_URL` = `postgresql://[user]:[pass]@[host]/[db]` (from Neon)
   - `S3_ENDPOINT` = `https://[account_id].r2.cloudflarestorage.com` (from Cloudflare R2)

### Step 2: Provision Database on Neon
1. Create a free PostgreSQL database at [neon.tech](https://neon.tech/).
2. Copy the connection string into `DATABASE_URL`.

### Step 3: Provision Storage on Cloudflare R2
1. Create a free bucket on Cloudflare R2.
2. Generate S3-compatible API credentials.

### Step 4: Verify Deployment & Health
Test health endpoints:
`curl https://[your-backend-url]/health` -> Should return `{"service":"respisense-ml","status":"ok"}`.
