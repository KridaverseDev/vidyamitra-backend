# AWS Elastic Beanstalk Deployment Guide

## Prerequisites

1. **AWS Account** - Sign up at https://aws.amazon.com
2. **AWS CLI** - Install from https://aws.amazon.com/cli/
3. **EB CLI** - Install Elastic Beanstalk CLI:
   ```bash
   pip install awsebcli
   ```

## Initial Setup

### 1. Configure AWS Credentials

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `ap-south-1` for Mumbai)
- Default output format: `json`

### 2. Initialize Elastic Beanstalk

```bash
eb init -p python-3.12 vidyamitra-backend --region ap-south-1
```

This will:
- Create `.elasticbeanstalk/` directory
- Set up your EB application

### 3. Create Environment

```bash
eb create vidyamitra-backend-prod
```

Or create with specific configuration:
```bash
eb create vidyamitra-backend-prod \
  --instance-type t3.small \
  --envvars APP_MODE=prod
```

## Environment Variables

Set environment variables in Elastic Beanstalk:

### Via EB CLI:
```bash
eb setenv SECRET_KEY="your-secret-key" \
  DB_NAME="your-db-name" \
  DB_USER="your-db-user" \
  DB_PASSWORD="your-db-password" \
  DB_HOST="your-db-host" \
  DB_PORT="5432" \
  GOOGLE_API_KEY="your-google-api-key" \
  PINECONE_INDEX_NAME="your-pinecone-index" \
  PINECONE_API_KEY="your-pinecone-api-key" \
  OPENAI_API_KEY="your-openai-api-key" \
  OPENAI_ORGANIZATION="your-openai-org" \
  AWS_ACCESS_KEY_ID="your-aws-access-key" \
  AWS_SECRET_ACCESS_KEY="your-aws-secret-key" \
  S3_BUCKET_NAME="your-s3-bucket-name" \
  BACKEND_HOST="https://your-app.elasticbeanstalk.com" \
  GENERATED_SLIDES_FOLDER="slides/generated/" \
  TEMPLATE_FOLDER="slides/template/base.pptx" \
  ALLOWED_HOSTS="your-app.elasticbeanstalk.com,your-custom-domain.com" \
  DEBUG="False"
```

### Via AWS Console:
1. Go to Elastic Beanstalk → Your Environment → Configuration
2. Software → Environment properties
3. Add all environment variables

## Deploy

### Deploy to Elastic Beanstalk:
```bash
eb deploy
```

### Deploy specific version:
```bash
eb deploy vidyamitra-backend-prod
```

## Post-Deployment

### 1. Check Application Status
```bash
eb status
```

### 2. View Logs
```bash
eb logs
```

### 3. SSH into Instance
```bash
eb ssh
```

### 4. Create Superuser (if needed)
```bash
eb ssh
python silicon/_microservices/admin/manage.py createsuperuser
```

### 5. Run Additional Setup Commands
```bash
eb ssh
python silicon/_microservices/admin/manage.py setup_knowledge
```

## Useful Commands

- **Check health**: `eb health`
- **Open in browser**: `eb open`
- **List environments**: `eb list`
- **Terminate environment**: `eb terminate`
- **View events**: `eb events`
- **Scale up**: `eb scale 2`

## Configuration Files

- `.ebextensions/01_python.config` - Python/WSGI configuration
- `.ebextensions/02_django.config` - Django migrations and static files
- `.ebextensions/03_nginx.config` - Nginx configuration
- `.ebextensions/04_environment.config` - Environment settings
- `Procfile` - Process definition for gunicorn

## Troubleshooting

1. **Check logs**: `eb logs`
2. **Check health**: `eb health`
3. **SSH and debug**: `eb ssh`
4. **View recent events**: `eb events --follow`
5. **Check environment variables**: `eb printenv`

## Database Connection

Make sure your RDS PostgreSQL security group allows connections from your Elastic Beanstalk security group.

## Static Files

Static files are collected during deployment and served via S3 (configured in `base.py`).

## Custom Domain

1. Go to Elastic Beanstalk → Your Environment → Configuration
2. Load balancer → Add listener (HTTPS)
3. Add SSL certificate
4. Update `ALLOWED_HOSTS` environment variable

