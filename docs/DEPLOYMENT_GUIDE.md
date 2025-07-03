# Deployment Guide

## Automated Deployment with Verification

Use the automated deployment script that includes verification:

```bash
# Deploy devQ branch to devq environment
./scripts/deploy.sh devq devQ

# Deploy main branch to prod environment  
./scripts/deploy.sh prod main

# Deploy specific branch to devr environment
./scripts/deploy.sh devr feature-branch
```

## Manual Deployment Steps

If you need to deploy manually:

1. **Deploy to Heroku:**
   ```bash
   git push heroku devQ:main  # for devq
   git push heroku main:main  # for prod
   ```

2. **Verify deployment:**
   ```bash
   ./scripts/verify_deployment.sh devq   # for devq
   ./scripts/verify_deployment.sh prod   # for prod
   ```

## Environment URLs

- **DevQ**: https://mystocktrackerapp-devq-6cb9ce7e7076.herokuapp.com/
- **DevR**: https://mystocktrackerapp-devr-607807562777.herokuapp.com/
- **Prod**: https://mystocktrackerapp-prod-32618c8b4af1.herokuapp.com/

## Verification Script

The verification script automatically:
- Checks dyno status
- Tests app responsiveness (60s timeout)
- Reports response time
- Shows logs if deployment fails

## Best Practices

1. Always run tests before deployment
2. Use the automated deployment script
3. Verify deployment success before proceeding
4. Check logs if verification fails