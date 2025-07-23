# GitHub Actions CI/CD Automation Plan

## Overview
Automate the current 7-step manual deployment process with GitHub Actions, including a **MANDATORY UAT approval gate**.

## Current Manual Process (To Be Eliminated)
1. Run full test suite in dev branch
2. Assuming 100% test passing
3. Pull any updates from main
4. Run full test suite in dev again
5. Assuming 100% test passing
6. Push to main
7. Deploy main and sync everything with GitHub

## Proposed Automated Flow

### Trigger
- Push to `devQ` branch from local repository

### Automated Steps
1. **Test Job**
   - Install Python 3.12 and dependencies
   - Run full test suite: `python -m pytest`
   - If tests fail → Stop workflow
   - If tests pass → Continue

2. **Deploy DevQ Job** (Parallel with step 3)
   - Deploy to `mystocktrackerapp-devq.herokuapp.com`
   - Available for UAT testing

3. **UAT Approval Gate** ⏸️ **MANDATORY MANUAL STEP**
   - Workflow pauses after devQ deployment
   - User performs UAT on devQ environment
   - User explicitly approves via GitHub Actions interface
   - **Only approved deployments proceed to production**
   - **Direct deployments to production are strictly prohibited**

4. **Promote to Main Job** (After approval)
   - Checkout and pull latest main branch
   - Merge devQ into main
   - Push main to GitHub
   - Deploy main to production: `mystocktrackerapp-prod.herokuapp.com`

## Implementation Steps

### 1. GitHub Repository Setup
- [ ] Create "production" environment in GitHub repo settings
- [ ] Add required reviewers for production environment
- [ ] Add GitHub Secrets:
  - `HEROKU_API_KEY` (from Heroku account settings)
  - `HEROKU_EMAIL` (Heroku account email)
- [ ] Configure branch protection rules to prevent direct pushes to main

### 2. Workflow File
- [ ] Commit `.github/workflows/ci-cd.yml` to repository
- [ ] Push to GitHub to activate workflow

### 3. Testing
- [ ] Make a test commit to devQ
- [ ] Verify workflow triggers automatically
- [ ] Test UAT approval process
- [ ] Verify production deployment after approval

## Benefits
- **Eliminates 7-step manual process** → Single `git push origin devQ`
- **Prevents broken deployments** with automatic testing
- **Maintains quality control** with mandatory UAT approval gate
- **Ensures environment sync** automatically
- **Provides full audit trail** in GitHub Actions
- **Prevents unauthorized production deployments** with branch protection

## User Experience After Implementation
```bash
# Complete deployment workflow
git push origin devQ

# Wait for notification: "DevQ deployed, ready for UAT"
# Test on https://mystocktrackerapp-devq-6cb9ce7e7076.herokuapp.com/
# Go to GitHub Actions → Approve deployment
# Production automatically deploys
```

## Rollback Plan
- Keep existing manual scripts as backup
- Can disable GitHub Actions if needed
- Manual deployment process remains available
- For emergencies, follow the documented emergency rollback procedure

## Emergency Procedures
- In case of critical production issues, follow the emergency rollback procedure in `docs/emergency_rollback_procedure.md`
- Emergency procedures require explicit approval and documentation
- Even emergency actions must follow a controlled process

## Files Created
- `.github/workflows/ci-cd.yml` - Main workflow
- `scripts/deploy.sh` - Manual backup script
- `docs/emergency_rollback_procedure.md` - Emergency rollback procedure
- This documentation file