## Introduction
This project is a web app for tracking the performance of stock portfolios v. market indexes. It has been developed via agentic coding. This file sets the context for AI agents to work. 

## ⚠️ CRITICAL: PRODUCTION DEPLOYMENT POLICY
**DIRECT DEPLOYMENTS TO PRODUCTION ARE STRICTLY PROHIBITED**

All production deployments MUST follow the established CI/CD workflow with mandatory UAT approval:
1. Changes must be pushed to devQ or devR branches only
2. Automated tests must pass (100%)
3. Dev environment deployment must be successful
4. UAT approval must be explicitly granted via GitHub Actions interface
5. Only after UAT approval can changes be merged to main and deployed to production

**EMERGENCY ROLLBACKS:** In case of critical production issues, follow the emergency rollback procedure in `docs/emergency_rollback_procedure.md` which requires explicit approval and documentation.

## Preparation for the AI agent
1. The project has a docs folder with requirements, high-level design, component design, UI wire frames and more. Please reviews those docs prior to starting work. 
2. We're using Github for source control. We have three branches, main, devQ and devR. 
3. The three branches are deployed to Heroku as follows.
    1. Main is deployed here: https://mystocktrackerapp-prod-32618c8b4af1.herokuapp.com/
    and referred to as Prod. 
    2. devQ is deployed here: https://mystocktrackerapp-devq-6cb9ce7e7076.herokuapp.com/ and referred to as devQ. 
    3. devR is deployed here: https://mystocktrackerapp-devr-607807562777.herokuapp.com/dashboard and referred to as devR.
4. **CRITICAL** There is a file at /Users/craigrow/craigrow_code/MyStockTrackerApp_Q/docs/code-assist.script.mdwith further instructions for AI agents. 
5. Before starting any coding, please become familiar with all the documents mentioned above and confirm any details necessary.

## ⚠️ CRITICAL: Branch Synchronization Protocol
**ALWAYS sync your development branch with main before starting work to prevent merge conflicts:**

```bash
# Before starting ANY development work:
git checkout main
git pull origin main
git checkout devQ  # or devR
git merge main     # Sync with latest main changes

# If merge conflicts occur, resolve them BEFORE coding
# Then proceed with development
```

**After GitHub Actions deployment completes:**
```bash
# IMPORTANT: Sync local repo with GitHub after automated deployment
git checkout main && git pull origin main
git checkout devQ && git pull origin devQ
# GitHub Actions merges branches on GitHub, not locally
```

**Why this matters:**
- Prevents merge conflicts during automated deployments
- Ensures your branch has the latest production changes
- Avoids deployment failures in GitHub Actions
- Maintains clean git history
- **Local repo can be out of sync after GitHub Actions automated merges**

## Deployment Automation (GitHub Actions CI/CD)
1. **Automated Workflow**: Push to devQ or devR triggers GitHub Actions automation:
   - Tests run automatically (225+ tests must pass 100%)
   - Automatic deployment to respective dev environment
   - Deployment verification with health checks
   - **MANDATORY UAT approval gate before production deployment**
   - Automatic merge to main and production deployment after approval

2. **New Development Workflow**:
   ```bash
   # STEP 1: Always sync with main first
   git checkout main && git pull origin main
   git checkout devQ  # or devR
   git merge main     # Resolve any conflicts here
   
   # STEP 2: Complete development work
   # ... make your changes ...
   
   # STEP 3: Deploy
   git push origin devQ  # or devR
   # Wait for dev deployment notification
   # Test dev environment for UAT
   # MANDATORY: Approve via GitHub Actions interface
   # Production deploys automatically ONLY after UAT approval
   
   # STEP 4: Sync local with GitHub after deployment
   git checkout main && git pull origin main
   git checkout devQ && git pull origin devQ
   # This ensures local repo reflects GitHub Actions merges
   ```

3. **Multi-Agent Coordination**: Two AI agents work simultaneously on devQ and devR branches. UAT approval gates prevent conflicts, but coordination is important.

4. **Branch Sync Requirements**: 
   - **ALWAYS** sync dev branches with main before starting work
   - Check for recent main branch updates before each development session
   - Resolve any merge conflicts in dev environment, never in production workflow
   - **ALWAYS** pull latest changes after GitHub Actions deployment completes
   - Local repository may be out of sync with GitHub after automated merges

5. **Production Deployment Requirements**:
   - **NEVER** push directly to main branch
   - **NEVER** deploy directly to production environment
   - **ALWAYS** require UAT approval before production deployment
   - **ALWAYS** follow the established CI/CD workflow
   - **ALWAYS** document any emergency procedures that bypass normal workflow

6. **Documentation**: See `docs/automation/github-actions-cicd-plan.md` for complete automation details.

## Code Quality
1. We have an extensive test suite. Promotion from dev branches to main happens automatically after:
    1. All tests pass 100% (automated)
    2. Dev environment deploys successfully (automated)
    3. **UAT approval is explicitly granted (MANDATORY manual step)**
2. We have real users who have dependencies on Main. No breaking changes are acceptable in Main.
3. **CRITICAL**: Direct deployments to production bypass critical quality gates and are strictly prohibited.
4. All code changes must be thoroughly tested in the dev environment before UAT approval.
5. Any emergency procedures that bypass normal workflow must be documented and approved.


