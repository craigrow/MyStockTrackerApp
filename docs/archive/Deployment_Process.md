# Deployment Process

## Manual Deployment Verification (Temporary Solution)

After any deployment to Heroku, run this verification step to ensure the app is up and running:

### Quick Verification
```bash
# Verify devQ deployment
./scripts/verify_deployment.sh devq

# Verify devR deployment  
./scripts/verify_deployment.sh devr

# Verify production deployment
./scripts/verify_deployment.sh prod
```

### What the script does:
1. Checks dyno status
2. Makes a request to wake up the app (handles cold starts)
3. Reports response time and status
4. Shows recent logs if there are issues

### Expected behavior:
- First request may take 30+ seconds (cold start)
- Should return HTTP 200 status
- Subsequent requests should be fast

### If verification fails:
1. Check recent logs: `heroku logs --tail --app [app-name]`
2. Restart dyno: `heroku restart --app [app-name]`
3. Re-run verification script

## Deployment URLs
- **DevQ**: https://mystocktrackerapp-devq-6cb9ce7e7076.herokuapp.com/
- **DevR**: https://mystocktrackerapp-devr-607807562777.herokuapp.com/
- **Prod**: https://mystocktrackerapp-prod-32618c8b4af1.herokuapp.com/