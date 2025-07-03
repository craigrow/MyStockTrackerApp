#!/bin/bash

# Automated Deployment Script with Verification
# Usage: ./scripts/deploy.sh [devq|devr|prod] [branch]

ENV=${1:-devq}
BRANCH=${2:-devQ}

case $ENV in
    devq)
        HEROKU_APP="mystocktrackerapp-devq"
        ;;
    devr)
        HEROKU_APP="mystocktrackerapp-devr"
        ;;
    prod)
        HEROKU_APP="mystocktrackerapp-prod"
        ;;
    *)
        echo "Usage: $0 [devq|devr|prod] [branch]"
        exit 1
        ;;
esac

echo "🚀 Starting deployment to $ENV environment..."
echo "Branch: $BRANCH"
echo "Heroku App: $HEROKU_APP"

# Deploy to Heroku
echo "📦 Deploying to Heroku..."
git push heroku $BRANCH:main

if [ $? -ne 0 ]; then
    echo "❌ Deployment failed!"
    exit 1
fi

echo "✅ Deployment completed successfully!"

# Run verification script
echo "🔍 Running deployment verification..."
./scripts/verify_deployment.sh $ENV

if [ $? -eq 0 ]; then
    echo "🎉 Deployment verified successfully!"
else
    echo "⚠️ Deployment verification failed - check logs"
    exit 1
fi