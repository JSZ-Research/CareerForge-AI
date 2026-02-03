#!/bin/bash
# Configuration
acrName="careerforgeacr1770096724"
appName="career-forge-ai-1770096724"
resourceGroup="CareerForgeRG_CA"

echo "🚀 Updating Deployment with new Code..."

# 1. Login to ACR
az acr login --name $acrName

# 2. Build & Push (AMD64)
# Note: Using linux/amd64 explicitely just in case
acrServer="$acrName.azurecr.io"
imageName="$acrServer/careerforge-ai:v1"

echo "Rebuilding Image..."
docker build --platform linux/amd64 -t $imageName .
docker push $imageName

# 3. Restart App
echo "Restarting Web App..."
az webapp restart --name $appName --resource-group $resourceGroup

echo "✅ Update Complete! Please wait 5 mins."
