# Uptime Status — GitHub → Spinnaker → Render (Mac/kind demo)

This repo is a **ready-to-push** scaffold that demonstrates a full CI/CD flow:
**GitHub Actions → Spinnaker (running locally on Mac via kind) → Render Deploy Hooks**.

It deploys a tiny “Uptime Status” app with:
- **API** (FastAPI) — serves `/health`, `/targets`, `/metrics`
- **Worker** (Python) — pings configured URLs and (demo) logs results
- **Web** (static) — renders metrics from the API (demo shell)
- **Spinnaker** config (`k8s/spinnaker.yml`) using **MinIO** as Front50 storage
- **kind** cluster config (`k8s/kind-spinnaker.yaml`) for Apple Silicon
- **GitHub Actions** workflows that **trigger** the Spinnaker pipeline via webhook

> NOTE: The demo API uses in-memory storage. For a production version, switch to Postgres
> (worker writes rows; API reads summaries). This is kept simple so you can deploy immediately.

---

## Quick Start (Mac)

### 0) Prereqs
- Docker Desktop **or** Colima
- Homebrew: `brew install kind kubectl helm cloudflared`

### 1) Create kind cluster (Apple Silicon friendly)
```bash
kind create cluster --config k8s/kind-spinnaker.yaml
kubectl cluster-info --context kind-spinkind
```

### 2) Install MinIO (S3-compatible) — no persistence (fastest)
```bash
kubectl create ns minio
helm repo add bitnami https://charts.bitnami.com/bitnami
helm upgrade --install minio bitnami/minio -n minio   --set auth.rootUser=admin   --set auth.rootPassword=admin12345   --set defaultBuckets=spinnaker   --set mode=standalone   --set replicaCount=1   --set persistence.enabled=false

# (optional) open console
kubectl -n minio port-forward svc/minio-console 9090:9090
open http://localhost:9090  # admin/admin12345
```

### 3) Install Spinnaker Operator
```bash
kubectl create ns spinnaker-operator
kubectl create ns spinnaker

kubectl apply -n spinnaker-operator -f https://raw.githubusercontent.com/armory/spinnaker-operator/master/deploy/crds/all-crds.yaml
kubectl apply -n spinnaker-operator -f https://raw.githubusercontent.com/armory/spinnaker-operator/master/deploy/operator/armory-operator.yaml
kubectl -n spinnaker-operator get pods
```

### 4) Deploy Spinnaker
```bash
kubectl apply -f k8s/spinnaker.yml
kubectl -n spinnaker get pods -w
```

### 5) Open Spinnaker
```bash
# Deck (UI)
kubectl -n spinnaker port-forward svc/spin-deck 9000:9000
# Gate (API)
kubectl -n spinnaker port-forward svc/spin-gate 8084:8084
```
- UI: http://localhost:9000

### 6) Create a pipeline
In Deck UI:
- Create **Application**: `uptime-status`
- Create **Pipeline**: `Deploy Uptime App`
- **Triggers** → Add **Webhook**; **Source** = `github-actions` (enabled)

Add stages:
1. Manual Judgment — “Deploy API to STAGING?”
2. Webhook — POST → `<RENDER_HOOK_API_STAGING>`
3. Webhook — GET → `https://<api-staging>/health` (fail on non-2xx)
4. Manual Judgment — “Promote API to PROD?”
5. Webhook — POST → `<RENDER_HOOK_API_PROD>`
6. Webhook — GET → `https://<api-prod>/health`
7. (Optional) Worker/Web stages (same pattern)

### 7) Trigger from GitHub Actions
- Set repo secrets: `SPIN_TRIGGER_URL` (your Gate webhook URL), `SPIN_TOKEN` (if you add auth; optional for local)
- Push to `main` → Actions will POST to Spinnaker
- Or local test:  
  ```bash
  curl -X POST http://localhost:8084/webhooks/webhook/github-actions     -H 'Content-Type: application/json'     -d '{"hello":"world"}'
  ```

### 8) Render services (create in the Render dashboard)
- `uptime-api` (Docker) → copy its **Deploy Hook URL**
- `uptime-worker` (Docker, Background Worker) → copy **Deploy Hook URL**
- `uptime-web` (Static Site) → copy **Deploy Hook URL**

Paste those URLs into your Spinnaker **Webhook** stages.

---

## Repo Layout

```
uptime-status/
├─ api/
├─ worker/
├─ web/
├─ k8s/
└─ .github/workflows/
```

---

## Postgres Upgrade (later)

- Add a Render Postgres instance.
- Worker: write `{url, ts, ms, code}` rows.
- API: compute uptime% and p95 from recent rows and return them in `/metrics`.

