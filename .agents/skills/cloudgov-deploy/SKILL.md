---
name: cloudgov-deploy
title: "cloud.gov Deployment"
description: "Deploy applications to cloud.gov — sandbox setup, manifest generation, CI/CD pipeline"
status: canonical
tier: 2
last_updated: "2026-06-01"
load_priority: on-demand
audience: ["developers", "agents"]
triggers: ["deploy", "cloud.gov", "cloudgov", "push to cloud", "deploy to sandbox"]
dependencies: ["project-bootstrap"]
---

# Skill: cloud.gov Deployment

Deploy a federal application to cloud.gov — the FedRAMP-authorized platform available to all federal employees.

## When to Use

- Deploying any federal application
- User says "deploy to cloud.gov" or "push to sandbox"
- PROJECT_PLAN.md lists cloud.gov as the hosting platform

## Why cloud.gov

- **Free sandbox** for anyone with a .gov, .mil, or .fed.us email
- **FedRAMP Authorized** — inherits ~80% of NIST 800-53 controls
- **Zero infrastructure management** — no servers, no patches, no OS updates
- **cf push** deploys in minutes — no Kubernetes, no Terraform required for sandbox

## Procedure

### Step 1: Sandbox Account Setup

Guide the user through account creation:

```bash
# 1. Sign up at https://cloud.gov/sign-up/ with your .gov/.mil email
# 2. Install the CF CLI: https://docs.cloud.gov/platform/getting-started/quickstart-setup/
# 3. Login:
cf login -a api.fr.cloud.gov --sso
# 4. Visit the passcode URL shown, authenticate, paste the code
# 5. Target your sandbox:
cf target -o sandbox-<agency> -s <your-email-prefix>
```

**Note:** Sandbox contents are cleared every 90 days. For persistent deployments, the agency needs a cloud.gov organization.

### Step 2: Generate manifest.yml

Create a `manifest.yml` in the project root based on the tech stack from PROJECT_PLAN.md:

**Python (FastAPI/Flask/Django):**
```yaml
---
applications:
  - name: <project-name>
    memory: 256M
    instances: 1
    buildpacks:
      - python_buildpack
    command: gunicorn app:app
    env:
      DISABLE_COLLECTSTATIC: 1
    services: []
```

**Node.js/TypeScript:**
```yaml
---
applications:
  - name: <project-name>
    memory: 256M
    instances: 1
    buildpacks:
      - nodejs_buildpack
    command: npm start
    env:
      NODE_ENV: production
    services: []
```

**Go:**
```yaml
---
applications:
  - name: <project-name>
    memory: 128M
    instances: 1
    buildpacks:
      - go_buildpack
    env:
      GOVERSION: go1.22
    services: []
```

**Static site (Astro/Hugo/Jekyll):**
```yaml
---
applications:
  - name: <project-name>
    memory: 64M
    instances: 1
    buildpacks:
      - staticfile_buildpack
    path: dist/
```

### Step 3: Add Services (if needed)

Based on PROJECT_PLAN.md database choice:

```bash
# PostgreSQL
cf create-service aws-rds micro-psql <project-name>-db
# Then add to manifest.yml services list:
#   services:
#     - <project-name>-db

# S3 storage
cf create-service s3 basic <project-name>-s3

# Redis
cf create-service aws-elasticache-redis redis-dev <project-name>-redis
```

Services bind automatically via `VCAP_SERVICES` environment variable.

### Step 4: First Deploy

```bash
# From project root:
cf push

# Verify:
cf app <project-name>
curl https://<project-name>.app.cloud.gov/
```

### Step 5: Set Up CI/CD

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to cloud.gov

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd  # v6

      - name: Install CF CLI
        run: |
          curl -L "https://packages.cloudfoundry.org/stable?release=linux64-binary&version=v8&source=github" | tar -xz
          sudo mv cf8 /usr/local/bin/cf

      - name: Deploy to cloud.gov
        env:
          CF_USERNAME: ${{ secrets.CF_USERNAME }}
          CF_PASSWORD: ${{ secrets.CF_PASSWORD }}
          CF_ORG: ${{ secrets.CF_ORG }}
          CF_SPACE: ${{ secrets.CF_SPACE }}
        run: |
          cf login -a api.fr.cloud.gov -u "$CF_USERNAME" -p "$CF_PASSWORD" -o "$CF_ORG" -s "$CF_SPACE"
          cf push
```

**Required secrets:** Set these in GitHub repo Settings → Secrets:
- `CF_USERNAME` — cloud.gov service account username
- `CF_PASSWORD` — cloud.gov service account password
- `CF_ORG` — your cloud.gov organization
- `CF_SPACE` — your cloud.gov space

For sandbox deployments, use personal credentials (not ideal for CI — sandbox is for prototyping).

### Step 6: Verify Deployment

```bash
# Check app status
cf app <project-name>

# View recent logs
cf logs <project-name> --recent

# Check all apps in space
cf apps

# Scale if needed (not available in sandbox)
# cf scale <project-name> -i 2 -m 512M
```

## Security Considerations

- cloud.gov handles TLS termination — apps receive HTTP on port 8080
- Use `VCAP_SERVICES` for database credentials, never hardcode
- Sandbox apps are publicly accessible — don't deploy with real data
- For production: agency needs a cloud.gov organization with proper ATO
- All cloud.gov apps get automatic HTTPS with valid certificates

## What cloud.gov Inherits

By deploying to cloud.gov, your system inherits controls for:
- Physical security (PE family)
- Infrastructure maintenance (MA family)
- System communications protection (SC family, partial)
- Access control at the platform level (AC family, partial)

Your app is still responsible for: application-level access control, input validation, secrets management, and business logic security. The AGENTS.md and CODING_PRACTICES.md cover these.

## Verification

After deployment:
- [ ] App responds at https://<name>.app.cloud.gov/
- [ ] No errors in `cf logs`
- [ ] Database service bound (if applicable)
- [ ] CI/CD pipeline deploys on push (if configured)
- [ ] No secrets in manifest.yml or code
