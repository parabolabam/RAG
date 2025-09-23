# Digital Ocean Deployment Workflow

This repository includes an automated deployment workflow that can deploy Docker containers to Digital Ocean using either App Platform or Droplets.

## Features

- **Multi-application support**: Deploy `senpy-ai-news-report`, `ai-chatbot`, or `web` applications
- **Environment-based deployment**: Support for `staging` and `production` environments  
- **Flexible deployment targets**: Deploy to Digital Ocean App Platform or Droplets
- **Automatic Docker image building**: Builds and pushes images to Digital Ocean Container Registry
- **Manual and automatic triggers**: Deploy on push to main/production branches or manually via workflow dispatch

## Prerequisites

### Required Secrets

Configure the following secrets in your GitHub repository settings:

1. **DIGITALOCEAN_ACCESS_TOKEN** - Your Digital Ocean API token
2. **DO_REGISTRY_NAME** - Your Digital Ocean Container Registry name
3. **DATABASE_URL** - Database connection string (if needed by your app)
4. **OPENAI_API_KEY** - OpenAI API key (if needed by your app)

### Optional Secrets (for App Platform deployment)

5. **DO_APP_ID** - Digital Ocean App Platform app ID (if deploying to App Platform)

### Optional Secrets (for Droplet deployment)

6. **DO_DROPLET_HOST** - IP address of your Digital Ocean droplet
7. **DO_DROPLET_USER** - SSH username for the droplet (usually 'root')
8. **DO_DROPLET_SSH_KEY** - Private SSH key for accessing the droplet

## Usage

### Automatic Deployment

The workflow automatically triggers on:
- Push to `main` branch → deploys to staging
- Push to `production` branch → deploys to production

### Manual Deployment

1. Go to the Actions tab in your GitHub repository
2. Select "Deploy to Digital Ocean" workflow
3. Click "Run workflow"
4. Choose:
   - Application to deploy (senpy-ai-news-report, ai-chatbot, or web)
   - Environment (staging or production)

## Deployment Methods

### Digital Ocean App Platform (Recommended)

If you provide a `DO_APP_ID` secret, the workflow will deploy to Digital Ocean App Platform:
- Fully managed deployment
- Automatic scaling
- Built-in load balancing
- Easy monitoring and logs

### Digital Ocean Droplet

If you don't provide a `DO_APP_ID` but provide droplet credentials, the workflow will deploy via SSH:
- Direct deployment to your droplet
- More control over the environment
- Requires manual server setup

## Application-Specific Notes

### senpy-ai-news-report (Python FastAPI)
- Uses existing Dockerfile
- Exposes port 8000
- Health check endpoint: `/docs`

### ai-chatbot (Next.js)
- Uses generated Dockerfile optimized for Next.js
- Exposes port 3000
- Standalone output for smaller container size

### web (Next.js)
- Uses generated Dockerfile optimized for Next.js
- Exposes port 3000
- Includes React Native Web configuration

## Container Registry

Images are pushed to Digital Ocean Container Registry with tags:
- `latest` - Always points to the most recent build
- `<commit-sha>` - Specific commit identifier (first 8 characters)

## Environment Variables

The following environment variables are automatically set:
- `NODE_ENV=production`
- `DATABASE_URL` (from secrets)
- `OPENAI_API_KEY` (from secrets)

## Monitoring

The workflow provides:
- Build logs for troubleshooting
- Deployment summary with image details
- Container status on deployment target

## Troubleshooting

1. **Build failures**: Check the build logs in the GitHub Actions tab
2. **Registry login issues**: Verify `DIGITALOCEAN_ACCESS_TOKEN` and `DO_REGISTRY_NAME`
3. **Deployment failures**: Check app logs in Digital Ocean dashboard
4. **SSH deployment issues**: Verify droplet credentials and network access

## Security Notes

- Secrets are encrypted and only accessible during workflow execution
- SSH keys should use ed25519 or RSA format
- Regularly rotate access tokens and SSH keys
- Use least privilege principle for API tokens