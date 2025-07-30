# Emergency Rollback Procedure

## ⚠️ CRITICAL: This procedure is for emergency use only

This document outlines the procedure for emergency rollbacks when critical issues are detected in production. This procedure should **only** be used in genuine emergencies where the production application is severely impacted and immediate action is required.

## Prerequisites for Emergency Rollback

Before initiating an emergency rollback, the following conditions must be met:

1. **Documented Critical Issue**: A critical issue must be documented with clear evidence of production impact
2. **Approval Required**: Explicit approval must be obtained from the project owner or designated approver
3. **Notification**: All team members must be notified of the emergency rollback
4. **Documentation**: The issue, impact, and rollback plan must be documented

## Emergency Rollback Procedure

### 1. Document the Issue

```
Issue Description: [Detailed description of the issue]
Impact: [Description of the impact on users/system]
Urgency: [Explanation of why immediate rollback is necessary]
Approver: [Name of person who approved the emergency rollback]
```

### 2. Identify Rollback Target

Identify the last known good commit to roll back to:

```bash
# Check recent commit history
git log --oneline -n 20

# Identify the commit before the problematic changes
# Note the commit hash for the rollback target
```

### 3. Create Rollback Branch

```bash
# Create a new branch from the target commit
git checkout -b emergency-rollback-YYYY-MM-DD [target-commit-hash]

# Verify you're on the correct commit
git log --oneline -n 1
```

### 4. Execute Rollback

```bash
# Force push to main branch on GitHub
git push -f origin emergency-rollback-YYYY-MM-DD:main

# Force push to production Heroku app
git push -f heroku-prod emergency-rollback-YYYY-MM-DD:main
```

### 5. Verify Rollback

1. Check that the production application is functioning correctly
2. Verify that the critical issue has been resolved
3. Document the outcome of the rollback

### 6. Synchronize Local Repository

```bash
# Update local main branch
git checkout main
git fetch origin
git reset --hard origin/main

# Update local dev branches
git checkout devQ
git pull origin main
git checkout devR
git pull origin main
```

### 7. Post-Rollback Documentation

After the emergency rollback, complete the following documentation:

```
Rollback Date/Time: [Date and time of rollback]
Rolled Back From: [Commit hash/description that was rolled back]
Rolled Back To: [Commit hash/description that was restored]
Verification Results: [Results of post-rollback verification]
Next Steps: [Plan to properly fix the issue through normal CI/CD process]
```

## Post-Emergency Actions

1. **Root Cause Analysis**: Conduct a thorough investigation to determine how the issue occurred
2. **Process Improvement**: Identify how the CI/CD process can be improved to prevent similar issues
3. **Proper Fix**: Implement a proper fix through the normal CI/CD process with UAT approval
4. **Documentation**: Update documentation based on lessons learned

## Approval Log

Each emergency rollback must be logged here:

| Date | Issue | Rolled Back From | Rolled Back To | Approver | Documentation Link |
|------|-------|------------------|----------------|----------|-------------------|
| 2025-07-23 | Performance optimization regressions on Dashboard | 5913574 (Fix Dashboard regressions) | e927939 (Auto-merge devR to main) | [Approver Name] | [Link to detailed documentation] |

## Remember

**Emergency rollbacks bypass critical quality gates and should be used only in genuine emergencies.**

The normal CI/CD process with UAT approval is always preferred for all changes to production.
