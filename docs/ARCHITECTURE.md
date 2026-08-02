# Respisense-ML Architecture Documentation

Respisense-ML supports a **Dual Architecture Model** built strictly using **100% Free Forever** tools (no credit card required):

---

## Model 1: Cloud-Native & Free Presentation Architecture

Used for live presentation demos, interviews, and public portfolio showcases.

```mermaid
graph TB
    subgraph Client["Client Tier"]
        UI["Web Browser (Three.js / Canvas UI)"]
    end

    subgraph Hosting["100% Free Hosting Options"]
        Tunnel["Method 1: Pinggy / Localtunnel\n(Instant Public URL from Localhost)"]
        Render["Method 2: Render Free Web Service\n(respisense-ml.onrender.com)"]
        PA["Method 3: PythonAnywhere Free Tier\n(username.pythonanywhere.com)"]
    end

    subgraph FreeDB["100% Free Storage"]
        Neon[("Neon Postgres\n(Free SQL Storage)")]
        R2[("Cloudflare R2\n(10GB Free S3 Storage)")]
    end

    UI --> Tunnel
    UI --> Render
    UI --> PA
    Render --> Neon
    Render --> R2
```

---

## Model 2: Self-Hosted Docker Compose Architecture

Used for local development or self-hosting on any hardware/VPS.

```mermaid
graph TB
    subgraph Host["Docker Host (Local Machine / Free VPS)"]
        Proxy["Nginx Reverse Proxy\n(Port 80)"]
        Flask["Flask App Container\n(Port 8080)"]
        Postgres[("PostgreSQL Container\n(Port 5432)")]
        MinIO[("MinIO S3 Storage Container\n(Port 9000 / 9001)")]

        Proxy -->|"Forward /"| Flask
        Flask -->|"SQL Queries"| Postgres
        Flask -->|"S3 API Uploads"| MinIO
    end

    User["Client Browser"] --> Proxy
```

---

## Platform Comparison (100% Free Tier)

| Option | URL Type | Credit Card Required? | Best For |
|---|---|---|---|
| **Pinggy / Localtunnel** | Temporary Public HTTPS Link | **No** | **Live Interview Presentations** (Runs on localhost hardware with 0 limits) |
| **Render Web Service** | Permanent (`.onrender.com`) | **No** | Permanent Portfolio Link |
| **PythonAnywhere** | Permanent (`.pythonanywhere.com`) | **No** | Lightweight Flask Hosting |
| **Neon Postgres** | Database Connection String | **No** | Free PostgreSQL Database |
