# AI Agent Onboarding Guide - MyStockTrackerApp

## 🚀 Quick Start (5 minutes)

**New to this project? Start here for immediate effectiveness.**

### Step 1: Understand the Project
- **What**: High-performance stock portfolio tracking web app
- **Tech Stack**: Python Flask + PostgreSQL + Bootstrap 5 + Chart.js
- **Status**: Production-ready with real users, 90% performance improvement achieved
- **Key Features**: Multi-portfolio tracking, ETF comparison, real-time data, intelligent caching

### Step 2: Understand Our Primary Workflow
- **Primary**: Rapid UAT development → iterate → test → CI/CD
- **Rapid UAT Track**: 2-3 minute deployments for development and testing
- **Production Pipeline**: Final CI/CD after UAT validation

### Step 3: Follow the Development Process
- **ALWAYS** use the [code-assist script](https://code.amazon.com/packages/AmazonBuilderGenAIPowerUsersQContext/blobs/mainline/--/scripts/code-assist.script.md) for any coding tasks
- **ALWAYS** sync with main before starting work (critical for CI/CD)
- **ALWAYS** achieve 100% test pass rate for production pipeline

## 📋 Essential Reading Order (15 minutes total)

Read these documents in this exact order for maximum effectiveness:

### 1. **Project Context** (5 min)
- [`README.md`](../README.md) - Live demo, features, quick start guide
- [`/docs/CURRENT_IMPLEMENTATION.md`](./CURRENT_IMPLEMENTATION.md) - Complete technical overview

### 2. **Architecture & Requirements** (7 min)
- [`/docs/design/HIGH_LEVEL_DESIGN-2025-06-23.md`](./design/HIGH_LEVEL_DESIGN-2025-06-23.md) - System architecture
- [`/docs/requirements/REQUIREMENTS_SPEC-2025-06-23.md`](./requirements/REQUIREMENTS_SPEC-2025-06-23.md) - Requirements specification

### 3. **Development Process** (3 min)
- [Code-Assist Script](https://code.amazon.com/packages/AmazonBuilderGenAIPowerUsersQContext/blobs/mainline/--/scripts/code-assist.script.md) - **MANDATORY** development workflow
- [`/docs/automation/github-actions-cicd-plan.md`](./automation/github-actions-cicd-plan.md) - CI/CD automation

## 🚀 Development Environment Options

### Primary Workflow: Rapid UAT Development

**This is our standard development approach** - fast iteration in test environments followed by production CI/CD.

**Use Case**: Primary development workflow  
**Deployment Time**: ~2-3 minutes  
**Requirements**: None for UAT testing, full tests before CI/CD  

**UAT Environment Naming:**
- **devR branch work**: `mystocktrackerapp-testr`
- **devQ branch work**: `mystocktrackerapp-testq`
- Simple, clear naming - one test environment per development branch  

#### Complete Development Workflow:
```bash
# 1. Sync with origin
git checkout main && git pull origin main
git checkout devR && git pull origin devR

# 2. Create feature branch and make changes
git checkout -b feature/my-feature
# ... implement your changes using code-assist script ...

# 3. Deploy to rapid UAT environment for testing
heroku create mystocktrackerapp-testr
git push heroku feature/my-feature:main

# 4. Iterate and test in UAT environment
# ... make changes, commit, push to heroku, test, repeat ...

# 5. When satisfied with UAT testing, run full test suite locally
python -m pytest tests/ -v

# 6. If tests pass, push to GitHub to initiate CI/CD
git checkout devR
git merge feature/my-feature
git push origin devR
# This triggers automated CI/CD pipeline

# 7. Clean up UAT environment
heroku apps:destroy mystocktrackerapp-testr
```

#### When to Use This Workflow:
- ✅ **All development work** (this is the primary approach)
- ✅ Feature development and testing
- ✅ Bug fixes and improvements
- ✅ UI/UX changes
- ✅ API integration work
- ✅ Performance optimizations

### Alternative: Direct CI/CD Pipeline (For Simple Changes)

**Use Case**: Simple, well-understood changes that don't need UAT iteration  
**Deployment Time**: ~30 minutes (includes full test suite)  
**Requirements**: 100% test pass rate (339/339 tests)

#### Direct CI/CD Workflow:
```bash
# 1. Sync with main (CRITICAL)
git checkout main && git pull origin main
git checkout devR && git merge main

# 2. Use code-assist script for development
# ... make changes and run tests locally ...

# 3. Deploy through CI/CD pipeline
git push origin devR
# Wait for CI/CD, approve UAT, automatic production deployment
```

#### When to Use Direct CI/CD:
- ✅ Simple bug fixes with obvious solutions
- ✅ Documentation updates
- ✅ Configuration changes
- ✅ Changes you're confident about without UAT iteration

#### When NOT to Use Direct CI/CD:
- ❌ New features requiring iteration
- ❌ UI/UX changes needing visual testing
- ❌ Complex logic requiring debugging
- ❌ Integration work with external APIs
- ❌ Performance optimizations needing measurement

### Option 2: Full CI/CD Pipeline (Existing - For Production Quality)

**Use Case**: Production-ready deployments  
**Deployment Time**: ~30 minutes (includes full test suite)  
**Requirements**: 100% test pass rate (339/339 tests)

#### Production Environments:
1. **Main** is deployed here: https://mystocktrackerapp-prod-32618c8b4af1.herokuapp.com/ (Production)
2. **devQ** is deployed here: https://mystocktrackerapp-devq-6cb9ce7e7076.herokuapp.com/ (Development)
3. **devR** is deployed here: https://mystocktrackerapp-devr-607807562777.herokuapp.com/dashboard (Development)

#### When to Use:
- ✅ Final testing before production
- ✅ Features that affect core business logic
- ✅ Changes that require comprehensive testing
- ✅ Production deployments
- ✅ Code that will be used by real users

## ⚠️ CRITICAL: Production Deployment Policy

**DIRECT DEPLOYMENTS TO PRODUCTION ARE STRICTLY PROHIBITED**

All production deployments MUST follow the established CI/CD workflow with mandatory UAT approval:
1. Changes must be pushed to devQ or devR branches only
2. Automated tests must pass (100%)
3. Dev environment deployment must be successful
4. UAT approval must be explicitly granted via GitHub Actions interface
5. Only after UAT approval can changes be merged to main and deployed to production

**EMERGENCY ROLLBACKS:** In case of critical production issues, follow the emergency rollback procedure in `docs/emergency_rollback_procedure.md` which requires explicit approval and documentation.

## ⚠️ CRITICAL: Branch Synchronization Protocol

**ALWAYS sync your development branch with main before starting work to prevent merge conflicts:**

### For Production Pipeline (devQ/devR):
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

### For Rapid UAT Environments:
```bash
# No special branch requirements - work from any branch
git checkout -b feature/quick-test
# ... make changes ...
git push heroku feature/quick-test:main
```

**Why this matters:**
- Prevents merge conflicts during automated deployments
- Ensures your branch has the latest production changes
- Avoids deployment failures in GitHub Actions
- Maintains clean git history
- **Local repo can be out of sync after GitHub Actions automated merges**

## 🎯 Recommended Workflows for AI Agents

### Primary Workflow: Rapid UAT Development (Use This for Most Work)
```bash
# 1. Sync with origin
git checkout main && git pull origin main
git checkout devR && git pull origin devR

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Use code-assist script for development
# Parameters:
# - task_description: "Your feature description"
# - mode: "interactive" (recommended)
# - repo_root: current directory
# - documentation_dir: "docs"

# 4. Deploy to UAT environment for testing
heroku create mystocktrackerapp-testr
git push heroku feature/my-feature:main

# 5. Iterate and test in UAT environment
# ... make changes, commit, push to heroku, test, repeat ...
# This is where you do most of your development and debugging

# 6. When satisfied with UAT testing, run full test suite locally
python -m pytest tests/ -v

# 7. If tests pass, push to GitHub to initiate CI/CD
git checkout devR
git merge feature/my-feature
git push origin devR
# This triggers automated CI/CD pipeline

# 8. Clean up UAT environment
heroku apps:destroy mystocktrackerapp-testr
```

### Alternative Workflow: Direct CI/CD (For Simple Changes Only)
```bash
# 1. Sync with main (CRITICAL)
git checkout main && git pull origin main
git checkout devR && git merge main

# 2. Use code-assist script for development
# Parameters:
# - task_description: "Your feature description"
# - mode: "interactive"
# - repo_root: current directory
# - documentation_dir: "docs"

# 3. Run tests locally
python -m pytest tests/ -v

# 4. Deploy through CI/CD pipeline
git push origin devR
# Wait for CI/CD, approve UAT, automatic production deployment
```

## 🛠️ Code-Assist Script Integration

### For ANY Coding Task:
1. **Use the code-assist script** - This is MANDATORY, not optional
2. **Choose appropriate mode based on development track**

### Standard Parameters:
```
- task_description: "What you need to implement"
- repo_root: "/Users/craigrow/craigrow_code/MyStockTrackerApp_R"
- documentation_dir: "docs"
```

### Mode Selection:
**For Primary Rapid UAT Workflow:**
- `mode`: "interactive" (recommended for most development)
- Develop with UAT iteration and testing
- Run full tests before CI/CD push
- Complete documentation for production changes

**For Direct CI/CD (Simple Changes):**
- `mode`: "interactive" 
- Full TDD workflow with comprehensive testing
- Complete documentation and validation
- Thorough code review process

## 📝 Documentation Maintenance Requirements

### When to Update CURRENT_IMPLEMENTATION.md:
**REQUIRED for Production Pipeline:**
- ✅ New features or major functionality changes
- ✅ Architecture or data model changes  
- ✅ New API endpoints or services
- ✅ Performance optimizations or caching changes
- ✅ New dependencies or technology additions

**NOT REQUIRED for:**
- ❌ Bug fixes that don't change functionality
- ❌ UI/styling changes without logic changes
- ❌ Test additions or improvements
- ❌ Minor refactoring without architectural impact
- ❌ Rapid UAT experiments (unless transitioning to production)

### How to Update:
1. **Add new sections** for new features/services
2. **Update existing sections** for modified functionality  
3. **Update metrics** (test counts, performance numbers)
4. **Keep it current** - reflect the actual implementation state

### Documentation Update Process:
```bash
# After implementing changes in production pipeline:
1. Update CURRENT_IMPLEMENTATION.md with your changes
2. Commit documentation updates with your code changes
3. Include documentation updates in your commit message
   Example: "feat: add portfolio export feature + update docs"
```

## 🎯 Key Success Factors

### 1. **Quality Standards**
- **Production Pipeline**: 100% test pass rate (currently 339/339 tests passing)
- **Rapid UAT**: Focus on functionality, testing comes later in production pipeline
- **No breaking changes** in main branch (real users depend on it)
- **Follow existing patterns** (see CURRENT_IMPLEMENTATION.md)

### 2. **Performance Requirements**
- **Dashboard loads in 2-3 seconds** (90% improvement achieved)
- **Use intelligent caching** (40,000+ cached price records)
- **Market-aware data management** (different strategies for market hours)

### 3. **Architecture Principles**
- **Smart caching with market awareness**
- **Progressive loading for performance**
- **Comprehensive error handling**
- **Data integrity protection** (duplicate detection, validation)

## 📊 Current Project Status

### ✅ **Completed Features**
- Multi-portfolio management with real-time performance tracking
- ETF comparison (VOO/QQQ) with real dividend data
- Cash flow analysis with IRR calculations
- Intelligent caching system (90% performance improvement)
- CSV import/export with duplicate detection
- Chart visualization with date filtering
- Comprehensive test suite (339 tests, 100% pass rate)

### 🔧 **Technical Highlights**
- **Performance**: 2-3 second dashboard loading (vs 30+ seconds before)
- **Reliability**: 100% test coverage, zero production failures
- **Data Quality**: Duplicate prevention, comprehensive validation
- **User Experience**: Real-time feedback, progressive loading

## 🚨 Common Pitfalls to Avoid

### 1. **Branch Management**
- ❌ Never work directly on main
- ❌ Never skip the main branch sync before starting production pipeline work
- ❌ Never push to production without UAT approval
- ✅ Rapid UAT environments can work from any branch

### 2. **Code Quality**
- ❌ Never commit code with failing tests to production pipeline
- ❌ Never skip the code-assist script workflow
- ❌ Never break existing functionality
- ✅ Rapid UAT allows experimental code for testing

### 3. **Performance**
- ❌ Never add blocking operations to dashboard loading
- ❌ Never ignore caching strategies
- ❌ Never make unnecessary API calls during market hours

### 4. **Environment Management**
- ❌ Never leave UAT environments running indefinitely
- ❌ Never use UAT environments for production data
- ❌ Never confuse UAT and production environment URLs

## 🎯 Decision Matrix: Which Development Approach?

| Scenario | Primary: Rapid UAT → CI/CD | Alternative: Direct CI/CD |
|----------|---------------------------|---------------------------|
| New feature development | ✅ | ❌ |
| UI/UX changes | ✅ | ❌ |
| API integration work | ✅ | ❌ |
| Complex bug fixes | ✅ | ❌ |
| Performance optimizations | ✅ | ❌ |
| Database schema changes | ✅ | ❌ |
| Simple bug fixes | ✅ (still recommended) | ✅ |
| Documentation updates | ✅ (still recommended) | ✅ |
| Configuration changes | ✅ (still recommended) | ✅ |

**Default Choice**: Use the **Primary Rapid UAT → CI/CD workflow** for almost all development work.

## 📚 Deep Dive Resources (When Needed)

### Architecture & Design
- [`/docs/design/HIGH_LEVEL_DESIGN-2025-06-23.md`](./design/HIGH_LEVEL_DESIGN-2025-06-23.md)
- [`/docs/requirements/REQUIREMENTS_SPEC-2025-06-23.md`](./requirements/REQUIREMENTS_SPEC-2025-06-23.md)

### Implementation Details
- [`/docs/PERFORMANCE_OPTIMIZATION_SUMMARY.md`](./PERFORMANCE_OPTIMIZATION_SUMMARY.md)
- [`/docs/TESTING_FINAL_SUMMARY.md`](./TESTING_FINAL_SUMMARY.md)

### Deployment & Operations
- [`/docs/DEPLOYMENT_GUIDE.md`](./DEPLOYMENT_GUIDE.md)
- [`/docs/emergency_rollback_procedure.md`](./emergency_rollback_procedure.md)

## 🎯 Quick Reference Commands

### Primary Development Workflow:
```bash
# Sync and create feature branch
git checkout main && git pull origin main
git checkout devR && git pull origin devR
git checkout -b feature/my-feature

# Deploy to UAT for development
heroku create mystocktrackerapp-testr
git push heroku feature/my-feature:main

# After UAT iteration, test and push to CI/CD
python -m pytest tests/ -v
git checkout devR && git merge feature/my-feature
git push origin devR

# Clean up
heroku apps:destroy mystocktrackerapp-testr
```

### Alternative: Direct CI/CD:
```bash
# Sync and deploy
git checkout main && git pull origin main
git checkout devR && git merge main
python -m pytest tests/ -v
git push origin devR
```

### Verify Environment:
```bash
# Check test suite
python -m pytest tests/ -v

# Check branch status
git status && git branch -a

# Check Heroku apps
heroku apps
```

## 🎯 Ready to Start?

### Checklist:
1. ✅ Read this document completely
2. ✅ Review the code-assist script
3. ✅ Choose your development track (Rapid UAT vs Production Pipeline)
4. ✅ Sync your branch with main (if using production pipeline)
5. ✅ Run the test suite to verify everything works
6. ✅ Use the code-assist script for your first task

**Remember**: 
- **Primary Workflow**: Rapid UAT development → iterate → test → CI/CD (use this for most work)
- **Alternative**: Direct CI/CD for simple, well-understood changes
- **Code-assist script**: Your guide for ALL development work
- **Always run full tests** before pushing to CI/CD pipeline

---

**Questions?** Refer to the detailed documentation linked above or ask for clarification on specific aspects.

**Ready to code?** Choose your track, start with the code-assist script, and follow the appropriate workflow!
