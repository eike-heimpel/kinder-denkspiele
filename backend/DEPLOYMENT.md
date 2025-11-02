# Deploying Märchenweber Backend to Fly.io

This guide covers deploying the FastAPI backend to Fly.io and connecting it to your SvelteKit frontend.

## Prerequisites

- Fly.io account (sign up at https://fly.io)
- `flyctl` CLI installed
- Backend tested locally

## Installation

### 1. Install flyctl

**macOS:**
```bash
brew install flyctl
```

**Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows:**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### 2. Authenticate

```bash
fly auth login
```

This will open your browser to complete authentication.

---

## Initial Deployment

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Launch the App

```bash
fly launch
```

This command will:
- Auto-detect your FastAPI application
- Ask for an app name (e.g., `maerchenweber`)
- Select a region (choose closest to your users)
- Generate `fly.toml` configuration file
- Generate optimized multi-stage Dockerfile
- Ask if you want to deploy now (say **yes**)

**Example interaction:**
```
? Choose an app name (leaving blank will default to 'backend-...') maerchenweber
? Choose a region for deployment: Frankfurt, Germany (fra)
Created app 'maerchenweber' in organization 'personal'
...
? Would you like to deploy now? Yes
```

### 3. Set Environment Secrets

After deployment, set your environment variables:

```bash
# MongoDB connection string
fly secrets set MONGODB_URI="mongodb+srv://mongodb:HzjPZmYdslhDQdby@cluster0.c6qg4eq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# OpenRouter API key for LLM
fly secrets set OPENROUTER_API_KEY="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"

# API key for SvelteKit authentication (choose your own secure key)
fly secrets set API_KEY="your-secure-random-api-key-here"

# Optional: Allowed CORS origins (comma-separated, if needed beyond localhost)
fly secrets set ALLOWED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

**Security Note:** Generate a strong random API key:
```bash
# Generate a secure random API key
openssl rand -base64 32
```

### 4. Verify Deployment

Get your app URL:
```bash
fly status
```

Test the health endpoint:
```bash
curl https://maerchenweber.fly.dev/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "maerchenweber-api",
  "version": "1.0.0"
}
```

---

## Configure SvelteKit Frontend

### 1. Update Environment Variables

Add to your **root** `.env` file (not the backend directory):

```bash
# Production FastAPI URL
MAERCHENWEBER_API_URL=https://maerchenweber.fly.dev

# API key (must match the one set in Fly.io secrets)
MAERCHENWEBER_API_KEY=your-secure-random-api-key-here
```

**Important:**
- For **local development**, do NOT set these variables (or comment them out)
- The code will automatically use `http://localhost:8000` when these are not set

### 2. Verify Frontend Connection

Start your SvelteKit dev server:
```bash
npm run dev
```

The frontend should now:
- Use `http://localhost:8000` in local development
- Use `https://maerchenweber.fly.dev` when environment variables are set

---

## Subsequent Deployments

After making changes to the backend:

```bash
cd backend
fly deploy
```

This will:
- Build a new Docker image
- Deploy to Fly.io
- Restart the app with zero downtime

---

## Local Development Workflow

### Running Both Servers Locally

**Terminal 1 - SvelteKit Frontend:**
```bash
npm run dev
```

**Terminal 2 - FastAPI Backend:**
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

**Environment Setup:**
- `.env` should NOT have `MAERCHENWEBER_API_URL` or `MAERCHENWEBER_API_KEY`
- Frontend will use `http://localhost:8000`
- Backend will NOT require API key authentication

---

## Production Deployment

When deploying to production:

### 1. Set Environment Variables

Ensure your production `.env` has:
```bash
MAERCHENWEBER_API_URL=https://maerchenweber.fly.dev
MAERCHENWEBER_API_KEY=your-secure-random-api-key-here
```

### 2. Deploy SvelteKit

Deploy your SvelteKit app to your hosting platform (Vercel, Netlify, etc.)

### 3. Update CORS (if needed)

If your production SvelteKit domain is different from localhost, update the CORS settings:

```bash
fly secrets set ALLOWED_ORIGINS="https://yourdomain.com"
```

---

## Monitoring & Debugging

### View Logs

```bash
fly logs
```

### SSH into the App

```bash
fly ssh console
```

### Check App Status

```bash
fly status
```

### View Secrets (names only, not values)

```bash
fly secrets list
```

### Scale the App

```bash
# Scale to 2 machines for high availability
fly scale count 2

# Change machine type
fly scale vm shared-cpu-2x
```

---

## Environment Variables Reference

### Backend (Fly.io Secrets)

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGODB_URI` | Yes | MongoDB Atlas connection string |
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for LLM calls |
| `API_KEY` | Production | API key for SvelteKit authentication |
| `ALLOWED_ORIGINS` | Optional | Additional CORS origins (comma-separated) |

### Frontend (SvelteKit .env)

| Variable | Required | Description |
|----------|----------|-------------|
| `MAERCHENWEBER_API_URL` | Production | Fly.io app URL (omit for local dev) |
| `MAERCHENWEBER_API_KEY` | Production | API key matching backend (omit for local dev) |

---

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use strong random API keys** (32+ characters)
3. **Rotate keys periodically** using `fly secrets set`
4. **Monitor logs** for unauthorized access attempts
5. **Use HTTPS only** in production (Fly.io provides this automatically)
6. **Restrict CORS** to your specific domains in production

---

## Troubleshooting

### Issue: "Invalid or missing API key" error

**Solution:**
- Verify API key matches in both Fly.io secrets and SvelteKit `.env`
- Check `fly secrets list` to confirm `API_KEY` is set
- Restart Fly.io app after setting secrets: `fly deploy`

### Issue: CORS errors in production

**Solution:**
- Add your production domain to `ALLOWED_ORIGINS`:
  ```bash
  fly secrets set ALLOWED_ORIGINS="https://yourdomain.com"
  ```

### Issue: Backend not connecting to MongoDB

**Solution:**
- Verify `MONGODB_URI` secret is set correctly
- Check MongoDB Atlas network access allows Fly.io IPs
- View logs: `fly logs`

### Issue: Local development using production API

**Solution:**
- Comment out or remove `MAERCHENWEBER_API_URL` and `MAERCHENWEBER_API_KEY` from `.env`
- Restart SvelteKit dev server

---

## Cost Estimation

Fly.io pricing (as of 2024):

- **Free tier:** 3 shared-cpu-1x VMs with 256MB RAM
- **Hobby plan:** $1.94/month for shared-cpu-1x with 256MB RAM
- **Scale up:** Adjust based on traffic

**Estimated cost:** Free to ~$2/month for low-traffic personal use

---

## Additional Resources

- [Fly.io Documentation](https://fly.io/docs/)
- [FastAPI Deployment Guide](https://fly.io/docs/python/frameworks/fastapi/)
- [Fly.io Python Basics](https://fly.io/docs/python/the-basics/)
- [Managing Secrets](https://fly.io/docs/apps/secrets/)

---

## Quick Reference

```bash
# Deploy
cd backend && fly deploy

# View logs
fly logs

# Set secret
fly secrets set KEY=value

# Check status
fly status

# Scale
fly scale count 2

# SSH
fly ssh console
```

---

**Your backend is now deployed to Fly.io and ready to serve your SvelteKit frontend!**
