#!/bin/bash

# Deployment Verification Script
# Usage: ./scripts/verify_deployment.sh [devq|devr|prod]

ENV=${1:-devq}

case $ENV in
    devq)
        URL="https://mystocktrackerapp-devq-6cb9ce7e7076.herokuapp.com/"
        APP="mystocktrackerapp-devq"
        ;;
    devr)
        URL="https://mystocktrackerapp-devr-607807562777.herokuapp.com/"
        APP="mystocktrackerapp-devr"
        ;;
    prod)
        URL="https://mystocktrackerapp-prod-32618c8b4af1.herokuapp.com/"
        APP="mystocktrackerapp-prod"
        ;;
    *)
        echo "Usage: $0 [devq|devr|prod]"
        exit 1
        ;;
esac

echo "🚀 Verifying $ENV deployment..."
echo "URL: $URL"

# Check dyno status
echo "📊 Checking dyno status..."
heroku ps --app $APP

# Wake up the app with a health check
echo "⏰ Waking up app (may take 30+ seconds)..."
START_TIME=$(date +%s)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 60 $URL)
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

if [ $HTTP_CODE -eq 200 ]; then
    echo "✅ App is responding (HTTP $HTTP_CODE) - took ${DURATION}s"
    echo "🌐 App URL: $URL"
else
    echo "❌ App failed to respond (HTTP $HTTP_CODE) after ${DURATION}s"
    echo "📋 Recent logs:"
    heroku logs --tail --num=10 --app $APP
    exit 1
fi