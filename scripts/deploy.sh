#!/bin/bash
# Simple deployment script for manual use

set -e

echo "🚀 Starting deployment workflow..."

# 1. Run tests in current branch
echo "📋 Running tests in current branch..."
RESULT=$(python -m pytest --tb=no -q | tail -1)
if [[ $RESULT != *"passed"* ]] || [[ $RESULT == *"failed"* ]]; then
  echo "❌ Tests failed: $RESULT"
  exit 1
fi
echo "✅ Tests passed: $RESULT"

# 2. Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# 3. If on devQ, merge to main
if [ "$CURRENT_BRANCH" = "devQ" ]; then
  echo "🔄 Merging devQ to main..."
  git checkout main
  git pull origin main
  git merge devQ --no-ff -m "Auto-merge devQ to main after tests pass"
  
  # 4. Run tests in main
  echo "📋 Running tests in main..."
  RESULT=$(python -m pytest --tb=no -q | tail -1)
  if [[ $RESULT != *"passed"* ]] || [[ $RESULT == *"failed"* ]]; then
    echo "❌ Tests failed in main: $RESULT"
    exit 1
  fi
  echo "✅ Tests passed in main: $RESULT"
  
  # 5. Push to GitHub
  echo "📤 Pushing to GitHub..."
  git push origin main
  git checkout devQ
  git push origin devQ
  
  # 6. Deploy to both environments
  echo "🚀 Deploying to production..."
  git checkout main
  git push heroku-prod main
  
  echo "🚀 Deploying to devQ..."
  git checkout devQ
  git push heroku devQ:main
  
  echo "✅ Deployment complete!"
else
  echo "⚠️  Not on devQ branch. Manual deployment only."
  echo "📤 Pushing current branch to GitHub..."
  git push origin $CURRENT_BRANCH
fi