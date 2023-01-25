#!/bin/bash

# Authentification
echo "Login and Authenticate..."
az login --output none
az account set \
    --subscription "for-flyme-project" \
    --output none

ma_localisation=westeurope
echo "done"

# Resource group creation
echo "resource group creation..."
az group create \
     --location $ma_localisation \
     --name botrg \
     --output none
echo "done"

#Luis resources creation
echo "Luis authoring resource..."
az cognitiveservices account create \
      -n luis-authoring  \
      -g botrg \
      --kind LUIS.Authoring \
      --sku F0 \
      -l $ma_localisation \
      --yes \
     --output none
echo "done"

echo "Luis prediction resource..."
az cognitiveservices account create \
      -n luis-pred \
      -g botrg \
      --kind LUIS \
      --sku F0 \
      -l $ma_localisation \
      --yes \
     --output none
echo "done"

sleep 10

# Luis API authentication key
echo "LuisAuthKey export..."
LuisAuthKey=$(az cognitiveservices account keys list \
                    --name luis-authoring \
                    --resource-group botrg \
                    --query key1 -o tsv)
export LuisAuthKey

# Create, train and publish luis app
python create_luis_app.py
luis set --authoringKey $LuisAuthKey
LuisAPPId=$(luis list apps --take 1 | grep -o -P -- '"id": "\K.{36}')
export LuisAPPId
echo "LuisAPPId export..."

# Addition of the prediction resource to the Luis app
echo "Addition of Luis prediction resource to Luis app..."
arm_access_token=$(az account get-access-token \
    --resource=https://management.core.windows.net/ \
    --query accessToken \
    --output tsv)

luis set \
    --appId $LuisAPPId \
    --versionId 0.1 \
    --region $ma_localisation

luis add appazureaccount \
    --in id.json \
    --appId $LuisAPPId --armToken $arm_access_token

LuisAPIKey=$(az cognitiveservices account keys list \
                    --name luis-pred \
                    -g botrg \
                    --query key1 -o tsv)
export LuisAPIKey
LuisAPIHostName="westeurope.api.cognitive.microsoft.com"
export LuisAPIHostName
echo "done"


# App service, Webapp and bot
# Registration
read -s -p 'Define your Microsoft App Passwords (please be careful to remember it) :' -r MicrosoftAppPassword
export MicrosoftAppPassword

echo "App registration..."
az ad app create \
     --display-name "flymebot2101" \
     --output none
echo "done"
echo "MicrosoftAppId export..."
MicrosoftAppId=$(az ad app list --display-name flymebot2101 | grep -o -P -- '"appId": "\K.{36}')
export MicrosoftAppId
echo "done"

# Service Plan
echo "App Service plan creation..."
az appservice plan create \
     -g botrg \
     -n flymebotserviceplan \
     --location $ma_localisation \
     --is-linux \
     --output none
echo "done"

# Web App
echo "web app creation..."
az webapp create \
     -g botrg \
     -p flymebotserviceplan \
     -n flymebot2101 \
     --runtime "python:3.9" \
     --output none
echo "done"


# App insights
echo "App Insights creation..."
az monitor app-insights component create \
     --app luis-app-ins \
     --location $ma_localisation \
     --kind web \
     -g botrg \
     --application-type web \
     --output none
InstrumentationKey=$(az monitor app-insights component show --app luis-app-ins --resource-group botrg --query instrumentationKey -o tsv)
echo "InstrumentationKey:"
echo $InstrumentationKey
export InstrumentationKey
echo "done"

#API Id and key App insights
echo "App Insights API Key creation..."
AI_API_KEY=$(az monitor app-insights api-key create \
    --api-key cle_bot \
    --app luis-app-ins \
    -g botrg \
    --read-properties ReadTelemetry \
    --query apiKey \
    -o tsv)
echo "AI_API_KEY:"
echo $AI_API_KEY
export AI_API_KEY

AI_APP_ID=$(az monitor app-insights component show \
    --app luis-app-ins \
    --resource-group botrg \
    --query appId \
    -o tsv)
echo "AI_APP_ID:"
echo $AI_APP_ID
export AI_APP_ID
echo "done"

#Bot creation
#echo "Bot creation..."
#az bot create \
#    --appid $MicrosoftAppId \
#    --app-type "MultiTenant" \
#    --name flymebotym \
#    --resource-group botrg \
#    --endpoint "https://flymebot202101.azurewebsites.net/api/messages" \
#    --output none
#echo "done"

#Link between bot and app insights
#echo "Bot telemetry settings update..."
#az bot update \
#    -n flymebotym \
#    -g botrg \
#    --ai-app-id $AI_APP_ID \
#    --ai-api-key $AI_API_KEY \
#    --ai-key $InstrumentationKey \
#    --output none
#echo "done"

#Deployment
# Web App config
echo "Web app settings update..."
az webapp config appsettings set \
      -n flymebot2101 \
      -g botrg \
      --settings InstrumentationKey=$InstrumentationKey \
                  LuisAPPId=$LuisAPPId \
                  LuisAPIKey=$LuisAPIKey \
                  LuisAPIHostName=$LuisAPIHostName \
                  MicrosoftAppId=$MicrosoftAppId \
                  MicrosoftAppPassword=$MicrosoftAppPassword \
                  WEBSITE_WEBDEPLOY_USE_SCM=true \
                  SCM_DO_BUILD_DURING_DEPLOYMENT=true \
      --output none

az webapp config set \
     -n flymebot2101 \
     -g botrg \
     --startup-file="python3.8 -m aiohttp.web -H 0.0.0.0 -P 8000 app:init_func" \
     --output none
echo "done"

# secrets definition to git hub secrets - used for unit tests during
echo "git hub secrets definition..."
gh auth login
gh secret set APP_ID --body $MicrosoftAppId \
            --repo "ym7ac1a/P10_chatbot"
gh secret set APP_PASSWORD --body $MicrosoftAppPassword \
            --repo "ym7ac1a/P10_chatbot"
gh secret set LUIS_APP_ID --body $LuisAppId \
            --repo "ym7ac1a/P10_chatbot"
gh secret set LUIS_API_KEY --body $LuisAPIKey \
            --repo "ym7ac1a/P10_chatbot"
gh secret set LUIS_API_HOST_NAME --body $LuisAPIHostName \
            --repo "ym7ac1a/P10_chatbot"
gh secret set APPINSIGHTS_INSTRUMENTATION_KEY --body $InstrumentationKey \
            --repo "ym7ac1a/P10_chatbot"

echo "get git hub access token..."
read -s -p 'Please enter your github access token: ' -r github_access_token
export github_access_token

# git hub actions defined
echo "git hub actions definition..."
az webapp deployment github-actions add \
      --repo "ym7ac1a/P10_chatbot" \
      -g botrg \
      -n flymebot2101 \
      -b master \
      --token $github_access_token

sleep 5

# Update publishing profile
echo "Publish profile update..."
gh secret set AZURE_WEBAPP_PUBLISH_PROFILE \
       --body "$(az webapp deployment list-publishing-profiles \
       --name flymebot2101 \
       --resource-group botrg \
       --xml)" \
       --repo "ym7ac1a/P10_chatbot"

echo "All good, you can now push on git to update the Bot."