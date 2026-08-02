# PRODUCTION DEPLOYMENT MASTER PLAYBOOK
A Universal, Reusable Deployment & DevOps Playbook for Full-Stack Software Projects

Paste this document into any future project as a standing reference for an AI coding assistant (Claude Code, Cursor, Codex, Gemini CLI, etc.) or a human engineer. It governs how the project gets deployed, secured, monitored, and scaled — never how the application looks or behaves.

## Table of Contents
[Introduction](#1-introduction) (includes [1.6 Applicability — What to Include vs. Skip](#16-applicability---what-to-include-vs-skip))
[Production Deployment Philosophy](#2-production-deployment-philosophy)
[Project Structure](#3-project-structure)
[Environment Variables](#4-environment-variables)
[Cloud Native Deployment](#5-cloud-native-deployment)
[Docker Deployment](#6-docker-deployment)
[Database Best Practices](#7-database-best-practices)
[Object Storage](#8-object-storage)
[Redis](#9-redis)
[Background Workers](#10-background-workers)
[Security](#11-security)
[Logging](#12-logging)
[Monitoring](#13-monitoring)
[Performance](#14-performance)
[CI/CD](#15-cicd)
[README Template](#16-readme-template)
[Deployment Architecture Diagrams](#17-deployment-architecture-diagrams)
[Interview Talking Points](#18-interview-talking-points)
[Production Checklist](#19-production-checklist)
[Common Deployment Mistakes](#20-common-deployment-mistakes)
[Troubleshooting Guide](#21-troubleshooting-guide)
[Scaling Strategy](#22-scaling-strategy)

## 1. Introduction
### 1.1 What this document is
This playbook is a deployment operating manual, not a design document. It exists to answer one question, repeatedly, across every project you ever ship: "How do I take working application code and make it run safely, reliably, and cheaply in production — without touching what the application does?"

It is written to be pasted at the start of a new project's deployment phase, read by either a human or an AI coding assistant, and followed mechanically. Every chapter is self-contained enough to be referenced individually ("go implement chapter 11") without re-reading the whole document.

### 1.2 What this document is not
This is not:
- A UI/UX guide
- A system design document for the application's business logic
- A framework tutorial
- A one-time deployment log for a specific project

If a task involves changing what a button does, how a page looks, what data a form collects, or how a feature behaves — that task does not belong in this playbook. Redirect it to normal feature development. This playbook only activates once the application already works and the question becomes "how do we ship it."

### 1.3 Who should use this
- AI coding assistants operating in agentic mode on a repository, told to "productionize this" or "deploy this."
- Solo developers and students building portfolio projects who want production-grade deployment without production-grade headcount.
- Small teams who don't yet have a dedicated DevOps/SRE hire and need a repeatable standard.

### 1.4 How to use this document
1. Read Chapter 2 (Philosophy) and the Critical Preservation Rules below before touching anything.
2. Read Chapter 3 to understand how the repository should be organized for deployment.
3. Pick one deployment architecture from Chapter 5 (Cloud Native) or Chapter 6 (Docker) — or implement both, since the application code doesn't change between them.
4. Work top-to-bottom through Chapters 7–15, implementing each concern (database, storage, caching, security, logging, monitoring, performance, CI/CD) incrementally, committing after each.
5. Use Chapter 19 as a final gate before calling anything "production ready."
6. Keep Chapters 20–22 as ongoing references — mistakes to avoid, a debugging companion, and a map of how the deployment should evolve as the project grows.

### 1.5 Critical Preservation Rules (read this first, every time)
This is the single most important section in the entire document. It overrides every other instruction if there is ever a conflict.

**The deployed application must look, feel, and behave exactly as it did before deployment work began.**

Concretely: an AI assistant or engineer working from this playbook may only touch deployment, infrastructure, security, performance, scalability, reliability, monitoring, logging, CI/CD, and documentation. It may never touch the UI, UX, layout, styling, branding, routing, page structure, business logic, API contracts, or feature set — because none of those are deployment concerns, and changing them while "just deploying" silently rewrites the product without anyone deciding to.

If, in the course of deployment work, a change to application code genuinely becomes unavoidable (for example: a hardcoded localhost URL must become an environment variable, or a missing /health route must be added for the orchestrator to function), the following procedure is mandatory before writing a single line:
1. State what the change is, precisely.
2. State why it's required — what breaks in production without it.
3. State the benefit of making the change.
4. State the risk of making the change.
5. State the alternative(s) considered, including "do nothing and accept X limitation."

Only then make the smallest possible backward-compatible change — never a rewrite, never a "while I'm in here" improvement, never a refactor of surrounding code.

A useful gut check: if a proposed change would be visible to an end user looking at the running application, it is very likely out of scope. If it's only visible in logs, infrastructure config, or a terminal, it is very likely in scope.

### 1.6 Applicability - What to Include vs. Skip
Not every chapter in this playbook applies to every project. Implementing infrastructure a project doesn't need is its own kind of production risk - it adds attack surface, cost, and operational burden with no corresponding benefit. Before starting work, classify each chapter using the table below and skip anything the project has no genuine requirement for.

| Chapter | Status | Applies when... | Safe to skip when... |
| :--- | :--- | :--- | :--- |
| 1-4 (Intro, Philosophy, Structure, Env Vars) | Always required | Every project, no exceptions | Never - these are the foundation everything else sits on |
| 5 (Cloud Native) | Conditional - pick 5 or 6 | The project will run on managed platforms (Vercel, Render, Railway, Neon, etc.) | The project is exclusively self-hosted via Docker |
| 6 (Docker) | Conditional - pick 5 or 6 | The project needs self-hosted or full-control deployment | The project is exclusively cloud-native/managed |
| 7 (Database) | Always required | The project has any persistent data store | Never - nearly every real application has a database |
| 8 (Object Storage) | Conditional | The project accepts file/image/document uploads or generates downloadable files | No user-generated or stored files exist anywhere in the app |
| 9 (Redis) | Conditional | The project needs caching, rate limiting, server-side sessions, or a job queue | The project has low traffic, uses stateless JWTs only, and has no background jobs |
| 10 (Background Workers) | Conditional | The project has slow, unreliable, or deferrable work (email, PDF generation, third-party API calls) | Every operation the app performs is fast and safe to do synchronously in the request cycle |
| 11 (Security) | Always required | Every project accepting any network traffic | Never - baseline security headers, input handling, and secret hygiene apply universally |
| 12 (Logging) | Always required | Every project | Never - even a small project needs structured logs to debug production issues |
| 13 (Monitoring) | Always required (Sentry/health checks); metrics conditional | Error tracking and health checks: always. Full Prometheus-style metrics: once traffic/team size justifies a dashboard | Metrics collection can be deferred for a solo portfolio project with minimal traffic |
| 14 (Performance) | Conditional, by sub-topic | Compression and caching: nearly always cheap and worth it. Image optimization: only if the app serves images. Code splitting/bundle analysis: only if the frontend bundle is large enough to matter | A tiny app with no images and a small bundle can defer most of this chapter |
| 15 (CI/CD) | Always required | Every project with more than a single manual deploy expected | Never - even solo projects benefit from automated lint/test/build gates |
| 16 (README Template) | Always required | Every project | Never - documentation is not optional |
| 17 (Diagrams) | Conditional | Onboarding a team, or documenting for an interview/portfolio audience | A private solo project with no other stakeholders can skip formal diagrams, though they remain good practice |
| 18 (Interview Talking Points) | Conditional | The project is a portfolio piece or the deployment will be discussed in an interview/review setting | Purely internal production systems with no such audience |
| 19 (Production Checklist) | Always required | Before any real production launch | Never - this is the final gate, always run it |
| 20-21 (Mistakes, Troubleshooting) | Always required as reference | Every project, as an ongoing reference | Never - keep both available even if not actively read line by line |
| 22 (Scaling Strategy) | Conditional, by stage | Only the stage matching the project's current size applies actively; later stages are read for awareness, not implemented early | Never implement Stage 3/4 tooling (multi-region, sharding, IaC) for a Stage 1 portfolio project - that is premature complexity, not thoroughness |

The governing rule: when a chapter's trigger condition genuinely doesn't exist in the project, skip that chapter's implementation entirely rather than adding the infrastructure "just in case." When in doubt, apply the same procedure as any other necessary change (Section 1.5) - state what's being skipped and why, so the decision is visible and reviewable, not silent.

## 2. Production Deployment Philosophy
### 2.1 Deployment is a separate concern from development
The application should be deployable because it was built to a set of portable conventions (environment-based config, statelessness, health endpoints) — not because deployment work reshapes the application to fit a particular platform. Good deployment work is almost always additive: new config files, new scripts, new infrastructure definitions, sitting alongside application code without invading it.

### 2.2 Boring technology first
Production systems should default to the most boring, well-documented, widely-supported option at every layer unless there's a concrete reason not to: managed Postgres over a self-hosted database cluster, a standard reverse proxy over a custom one, established CI/CD platforms over bespoke pipelines. Novelty is a cost paid in incident response, not a feature.

### 2.3 Twelve-Factor as a baseline, not a religion
This playbook borrows heavily from the [Twelve-Factor App](https://12factor.net/) methodology: config in the environment, strict separation of build/release/run stages, stateless processes, disposability, dev/prod parity. These principles are treated as strong defaults. Deviating from them is allowed when justified (see the change procedure in 1.5), not forbidden outright.

### 2.4 Everything reproducible, nothing tribal
A deployment that only works because one engineer remembers a manual step is a production incident waiting to happen. Every step in this playbook should end up codified: in a Dockerfile, in a CI workflow, in an infrastructure-as-code file, or in the README — never only in someone's memory.

### 2.5 Fail loud, fail early
Prefer configuration that fails at build time or startup time over configuration that fails silently at runtime under load. A missing environment variable should crash the container on boot with a clear error message, not undefined-propagate through the app until a user hits a broken feature.

### 2.6 Security and observability are not "later" tasks
They are treated in this playbook as first-class chapters (11–13), not appendices. A project without structured logs, health checks, and basic secret hygiene is not "done, minus polish" — it is not production ready, full stop.

### 2.7 Two architectures, one codebase
This playbook standardizes on supporting both a fully managed cloud-native deployment and a self-hosted Docker Compose deployment from the same application code. This is deliberate: it forces the application to be genuinely portable (no platform-specific lock-in baked into business logic), it gives you a cheap/managed option and a full-control option for different project stages, and it's an excellent way to demonstrate platform-engineering competence in a portfolio or interview setting.

## 3. Project Structure
### 3.1 Guiding principle
Deployment artifacts live in clearly separated, predictable locations, distinct from application source. Nothing about deployment tooling should require hunting through `src/` to find it, and nothing about deployment tooling should live inside `src/`.

### 3.2 Reference layout
```text
project-root/
├── apps/                 # or frontend/ + backend/ if not a monorepo
│   ├── frontend/
│   │   ├── src/
│   │   ├── public/
│   │   ├── Dockerfile
│   │   ├── .env.example
│   │   └── package.json
│   └── backend/
│       ├── src/
│       ├── Dockerfile
│       ├── .env.example
│       └── package.json
├── infra/
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.prod.yml
│   │   ├── nginx/
│   │   │   └── default.conf
│   │   └── .env.example
│   ├── cloud/
│   │   ├── vercel.json
│   │   ├── render.yaml
│   │   └── terraform/    # optional, if IaC is used
│   └── scripts/
│       ├── migrate.sh
│       ├── backup-db.sh
│       ├── restore-db.sh
│       └── seed.sh
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── deploy-frontend.yml
│       └── deploy-backend.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   ├── TROUBLESHOOTING.md
│   └── RUNBOOK.md
├── PRODUCTION_DEPLOYMENT_MASTER_PLAYBOOK.md
├── docker-compose.yml    # symlink or thin wrapper, if preferred at root
├── .env.example
├── .gitignore
└── README.md
```

### 3.3 Rules for this structure
1. `.env` files are never committed. Only `.env.example` files with placeholder values are committed. This is enforced in `.gitignore` and re-verified in CI (see Chapter 15).
2. Every service that gets containerized owns its own `Dockerfile`, colocated with its source, not centralized in `infra/`. Compose files reference them by relative path.
3. `infra/` owns orchestration, not application logic. If a script in `infra/scripts/` needs to embed business logic beyond "run this migration tool" or "call this backup command," that's a sign the logic belongs in the application instead.
4. `docs/` is deployment/ops documentation, separate from any product or API documentation that already exists elsewhere in the repo.
5. Monorepo vs. polyrepo doesn't change any of the above — only the path depth.

### 3.4 What never moves
Nothing in this chapter implies restructuring `src/`. If an existing project has a different but coherent structure, deployment tooling adapts to fit alongside it — the reference layout above is a default for new projects, not a mandate to reorganize existing ones. Reorganizing source code is an application change and falls under the Critical Preservation Rules in Chapter 1.

## 4. Environment Variables
### 4.1 The core rule
Nothing environment-specific is ever hardcoded. Not a database URL, not an API key, not a port number, not a feature flag, not a third-party service endpoint. If a value differs — or could plausibly ever differ — between local development, staging, and production, it belongs in an environment variable.

### 4.2 Naming conventions
| Convention | Example | Notes |
| :--- | :--- | :--- |
| SCREAMING_SNAKE_CASE | `DATABASE_URL` | Universal standard across virtually every runtime |
| Prefix by concern | `REDIS_URL`, `S3_BUCKET_NAME` | Groups related config, aids searchability |
| Public frontend vars get a framework-specific prefix | `NEXT_PUBLIC_API_URL`, `VITE_API_URL` | Required by most bundlers to expose vars to client-side code — anything without this prefix must never leak to the browser bundle |
| No secrets in `NEXT_PUBLIC_*` / `VITE_*` ever | — | These are compiled into the client bundle and are publicly readable |

### 4.3 Required files
| File | Committed? | Purpose |
| :--- | :--- | :--- |
| `.env` | No | Actual local secrets, gitignored |
| `.env.example` | Yes | Every variable name the app needs, with placeholder or dummy values, documented inline |
| `.env.production` | No | Never committed; production secrets live in the hosting platform's secret manager, not in a file |
| `.env.test` | Optional, yes| Safe to commit if it only contains non-sensitive test fixtures |

### 4.4 .env.example template
```env
# ---- App ----
NODE_ENV=development
PORT=4000

# ---- Database ----
DATABASE_URL=postgresql://user:password@localhost:5432/appdb

# ---- Redis ----
REDIS_URL=redis://localhost:6379

# ---- Auth ----
JWT_SECRET=replace_with_a_long_random_string
JWT_EXPIRES_IN=15m
REFRESH_TOKEN_SECRET=replace_with_a_different_long_random_string

# ---- OAuth (example: Google) ----
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# ---- Object Storage ----
S3_ENDPOINT=
S3_BUCKET_NAME=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
S3_REGION=auto

# ---- Monitoring ----
SENTRY_DSN=

# ---- Frontend-exposed (safe for browser) ----
NEXT_PUBLIC_API_URL=http://localhost:4000
```

### 4.5 Validation at startup
Environment variables should be validated once, at process boot, and the process should refuse to start if a required variable is missing or malformed. (Implementation depends on language/framework).

### 4.6 Secrets management by platform
| Platform | Where secrets live |
| :--- | :--- |
| Vercel | Project -> Settings -> Environment Variables |
| Render / Railway | Service -> Environment tab, or a linked secret group |
| Docker Compose (self-hosted) | A gitignored `.env` file next to `docker-compose.yml`, referenced via `env_file:` |
| Kubernetes | Secret objects, sourced from external managers |
| GitHub Actions | Repository or environment-scoped Encrypted Secrets |

### 4.7 Rotation and hygiene
- Rotate `JWT_SECRET`, database passwords, and third-party API keys on a schedule (e.g., every 90 days) and immediately on suspected compromise or offboarding of anyone with access.
- Never log environment variables, even at debug level. A single accidental `console.log(process.env)` in a shared logging sink is a common real-world leak vector.
- Use distinct secrets per environment. A staging leak should never compromise production.

## 5. Cloud Native Deployment (Model 1 Specification)

### 5.1 Architecture Overview
Model 1 provides a fully managed, production-like deployment intended for portfolio projects, placement interviews, recruiter demonstrations, and zero-maintenance production environments.

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
     Neon      Cloudflare R2   Upstash Redis
                    │
                    ▼
                 Sentry
```

### 5.2 Provider Selection Rules
- **Frontend:** **Vercel** (Global CDN, automatic HTTPS, preview deployments, GitHub integration). Fallback: **Cloudflare Pages**.
- **Backend:** **Google Cloud Run** (Container based, auto-scaling, scale to zero, HTTPS). Fallback: **Render**.
- **AI/ML Projects:** Evaluate resource limits. If project fits within Cloud Run free limits -> Cloud Run. If project exceeds limits -> Oracle Cloud Always Free VM or Model 2 Docker. Never assume Hugging Face Spaces is available on free tier.
- **Database Priority Engine:** 1. **Neon** (Default: Serverless Postgres) -> 2. **Supabase** (Integrated Auth/Storage) -> 3. **CockroachDB** (Distributed SQL).
- **Object Storage:** **Cloudflare R2** (10GB Free, $0 Egress Fees, S3 Compatible). Fallback: **Supabase Storage**.
- **Cache:** **Upstash Redis** (Serverless Redis for sessions, caching, rate limiting, AI memory). Fallback: Self-hosted Redis.
- **Monitoring:** **Sentry** (Runtime errors, stack traces, performance). Fallback: **Better Stack**.
- **CI/CD:** **GitHub Actions** (`ci.yml`, `deploy.yml`, `security.yml`, `release.yml`, `lint.yml`, `test.yml`).

## 6. Docker Deployment
(Section deferred to reference document)

## 7. Database Best Practices

### 7.1 Manual Database Setup & Provisioning
Production databases should be managed (e.g., Supabase, Neon, AWS RDS, Render Postgres). Self-hosting a database cluster manually on VMs introduces severe operational risk for backups, failover, and scaling.

**Configuration Steps:**
1. Provision the managed database instance via your provider's dashboard.
2. Retrieve the secure connection string (e.g., `postgres://user:password@host:port/dbname`).
3. Add this connection string to your production environment variables as `DATABASE_URL`. **Never** commit it to source control.

### 7.2 Migrations and Schema Management
- **Never modify schemas manually in production.** All changes must go through a migration script (e.g., Prisma, Alembic, Flyway).
- Run migrations during the deployment build step (e.g., in a CI pipeline or a Render Build Command: `npm run build && npm run migrate`).

### 7.3 Connection Pooling (Critical for Serverless)
If you are deploying to a serverless platform like Vercel, every incoming request may spawn a new execution environment, rapidly exhausting your database's connection limit.
- **Mandatory:** Use a connection pooler (like PgBouncer or Neon's built-in pooler).
- Connect to the pooled URL rather than the direct database URL in your serverless functions.

### 7.4 Backups & Security
- Enable **automated daily backups** and Point-in-Time Recovery (PITR) in your database provider's dashboard.
- Restrict database access via IP allowlisting, ensuring only your cloud provider's IPs (or VPC) can connect to the database.

## 8. Object Storage
(Section deferred to reference document)

## 9. Redis
(Section deferred to reference document)

## 10. Background Workers
(Section deferred to reference document)

## 11. Security
(Section deferred to reference document)

## 12. Logging
(Section deferred to reference document)

## 13. Monitoring
(Section deferred to reference document)

## 14. Performance
(Section deferred to reference document)

## 15. CI/CD
(Section deferred to reference document)

## 16. README Template
(Section deferred to reference document)

## 17. Deployment Architecture Diagrams
(Section deferred to reference document)

## 18. Interview Talking Points
(Section deferred to reference document)

## 19. Production Checklist
(Section deferred to reference document)

## 20. Common Deployment Mistakes
(Section deferred to reference document)

## 21. Troubleshooting Guide
(Section deferred to reference document)

## 22. Scaling Strategy
(Section deferred to reference document)
