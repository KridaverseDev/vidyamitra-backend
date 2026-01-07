# Fly.io Deployment Guide

## Prerequisites

1. Install Fly.io CLI: https://fly.io/docs/getting-started/installing-flyctl/
2. Sign up for Fly.io account: https://fly.io/app/sign-up
3. Login: `flyctl auth login`

## Initial Setup

1. **Create the app** (if not already created):
   ```bash
   flyctl launch
   ```
   - This will use the existing `fly.toml` configuration

2. **Create PostgreSQL database**:
   ```bash
   flyctl postgres create --name vidyamitra-db
   ```
   - Note the connection details

3. **Attach database to app**:
   ```bash
   flyctl postgres attach vidyamitra-db
   ```
   - This automatically sets `DATABASE_URL` environment variable

## Environment Variables

Set all required environment variables:

```bash
# Django Secret Key
flyctl secrets set SECRET_KEY="your-secret-key-here"

# Database (automatically set if you attached postgres)
# DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT are set from DATABASE_URL

# API Keys
flyctl secrets set GOOGLE_API_KEY="your-google-api-key"
flyctl secrets set PINECONE_INDEX_NAME="your-pinecone-index"
flyctl secrets set PINECONE_API_KEY="your-pinecone-api-key"
flyctl secrets set OPENAI_API_KEY="your-openai-api-key"
flyctl secrets set OPENAI_ORGANIZATION="your-openai-org"

# AWS S3 (for static/media files)
flyctl secrets set AWS_ACCESS_KEY_ID="your-aws-access-key"
flyctl secrets set AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
flyctl secrets set S3_BUCKET_NAME="your-s3-bucket-name"

# Firebase (if using)
flyctl secrets set FIREBASE_CRED_PATH="/app/firebase_prod.json"

# App Settings
flyctl secrets set BACKEND_HOST="https://your-app.fly.dev"
flyctl secrets set GENERATED_SLIDES_FOLDER="slides/generated/"
flyctl secrets set TEMPLATE_FOLDER="slides/template/base.pptx"

# Allowed Hosts (your Fly.io app URL)
flyctl secrets set ALLOWED_HOSTS="vidyamitra-backend.fly.dev"

# Debug (set to False for production)
flyctl secrets set DEBUG="False"
```

## Deploy

1. **Deploy the application**:
   ```bash
   flyctl deploy
   ```

2. **Check deployment status**:
   ```bash
   flyctl status
   ```

3. **View logs**:
   ```bash
   flyctl logs
   ```

## Post-Deployment

1. **Create superuser** (if needed):
   ```bash
   flyctl ssh console
   poetry run python silicon/_microservices/admin/manage.py createsuperuser
   ```

2. **Run any additional setup commands**:
   ```bash
   flyctl ssh console
   poetry run python silicon/_microservices/admin/manage.py setup_knowledge
   ```

3. **Collect static files** (if needed):
   ```bash
   flyctl ssh console
   poetry run python silicon/_microservices/admin/manage.py collectstatic --noinput
   ```

## Useful Commands

- **View app info**: `flyctl info`
- **SSH into app**: `flyctl ssh console`
- **View logs**: `flyctl logs`
- **Scale app**: `flyctl scale count 1`
- **Restart app**: `flyctl apps restart vidyamitra-backend`

## Database Management

- **Connect to database**: `flyctl postgres connect -a vidyamitra-db`
- **View database info**: `flyctl postgres list`

## Troubleshooting

1. **Check if app is running**: `flyctl status`
2. **View recent logs**: `flyctl logs --limit 100`
3. **SSH and debug**: `flyctl ssh console`
4. **Check environment variables**: `flyctl secrets list`

