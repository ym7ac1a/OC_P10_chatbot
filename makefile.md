
##### LUIS service #####
$ conda create -n flyme python=3.9

$ conda activate flyme

$ pip install -r txt.requirements

$ python src/create_luis_app.py

$ git clone https://github.com/Microsoft/botbuilder-samples.git

$ mv botbuilder-samples/samples/python/21.corebot-app-insights/ .

$ rm -r botbuilder-samples

$ pip install -r 21.corebot-app-insights/requirements.txt

# modify config.py
$ python 21.corebot-app-insights/app.py
# V3
https://flymeluisresource-authoring.cognitiveservices.azure.com/luis/prediction/v3.0/apps/d008c5e2-b0c9-4c5d-92f6-262897bdc0ac/slots/staging/predict?verbose=true&show-all-intents=true&log=true&subscription-key=8ad33ca9a5fb49589908dcede8f780b5&query=I%20want%20to%20book%20a%20trip%20from%20Paris
# V2
https://westeurope.api.cognitive.microsoft.com/luis/v2.0/apps/d008c5e2-b0c9-4c5d-92f6-262897bdc0ac?q=book flight London&subscription-key=8ad33ca9a5fb49589908dcede8f780b5



##### PUBLISH BOT #####
# create a resource group
$ az group create --name flyme-bis --location "France Central"
{
  "id": "/subscriptions/3c974ab8-79df-42de-9811-da7b581583ef/resourceGroups/flyme-bis",
  "location": "francecentral",
  "managedBy": null,
  "name": "flyme-bis",
  "properties": {
    "provisioningState": "Succeeded"
  },
  "tags": null,
  "type": "Microsoft.Resources/resourceGroups"
}

# create an identity resource
$ az ad app create --display-name "flyme-app"
{
  "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#applications/$entity",
  "addIns": [],
  "api": {
    "acceptMappedClaims": null,
    "knownClientApplications": [],
    "oauth2PermissionScopes": [],
    "preAuthorizedApplications": [],
    "requestedAccessTokenVersion": 2
  },
  "appId": "0fb031ca-5e68-4ae1-969e-2e4d004b318f",
  "appRoles": [],
  "applicationTemplateId": null,
  "certification": null,
  "createdDateTime": "2023-01-17T20:06:43.7220662Z",
  "defaultRedirectUri": null,
  "deletedDateTime": null,
  "description": null,
  "disabledByMicrosoftStatus": null,
  "displayName": "flyme-app",
  "groupMembershipClaims": null,
  "id": "f16e075a-5006-4d06-b393-cd5d5aeab3a4",
  "identifierUris": [],
  "info": {
    "logoUrl": null,
    "marketingUrl": null,
    "privacyStatementUrl": null,
    "supportUrl": null,
    "termsOfServiceUrl": null
  },
  "isDeviceOnlyAuthSupported": null,
  "isFallbackPublicClient": null,
  "keyCredentials": [],
  "notes": null,
  "optionalClaims": null,
  "parentalControlSettings": {
    "countriesBlockedForMinors": [],
    "legalAgeGroupRule": "Allow"
  },
  "passwordCredentials": [],
  "publicClient": {
    "redirectUris": []
  },
  "publisherDomain": "yohanmadecgmail.onmicrosoft.com",
  "requestSignatureVerification": null,
  "requiredResourceAccess": [],
  "samlMetadataUrl": null,
  "serviceManagementReference": null,
  "signInAudience": "AzureADandPersonalMicrosoftAccount",
  "spa": {
    "redirectUris": []
  },
  "tags": [],
  "tokenEncryptionKeyId": null,
  "verifiedPublisher": {
    "addedDateTime": null,
    "displayName": null,
    "verifiedPublisherId": null
  },
  "web": {
    "homePageUrl": null,
    "implicitGrantSettings": {
      "enableAccessTokenIssuance": false,
      "enableIdTokenIssuance": false
    },
    "logoutUrl": null,
    "redirectUriSettings": [],
    "redirectUris": []
  }
}

# create the app service
$ az deployment group create --resource-group "flyme-bis" --template-file 21.corebot-app-insights/deploymentTemplates/deployUseExistResourceGroup/template-BotApp-with-rg.json --parameters 21.corebot-app-insights/deploymentTemplates/deployUseExistResourceGroup/parameters-for-template-BotApp-with-rg.json 
Parameter persistence is turned on. Its information is saved in working directory /home/yo/Documents/OpenClassrooms/P10_chatbot. You can run `az config param-persist off` to turn it off.
Your preference of --resource-group: flyme-bis is now saved as persistent parameter. To learn more, type in `az config param-persist --help`
{
  "id": "/subscriptions/3c974ab8-79df-42de-9811-da7b581583ef/resourceGroups/flyme-bis/providers/Microsoft.Resources/deployments/template-BotApp-with-rg",
  "location": null,
  "name": "template-BotApp-with-rg",
  "properties": {
    "correlationId": "6db804e2-948e-4f22-bfa9-ff7cee0a9ec7",
    "debugSetting": null,
    "dependencies": [
      {
        "dependsOn": [
          {
            "id": "/subscriptions/3c974ab8-79df-42de-9811-da7b581583ef/resourceGroups/flyme-bis/providers/Microsoft.Web/serverfarms/flyme-plan",
            "resourceGroup": "flyme-bis",
            "resourceName": "flyme-plan",
            "resourceType": "Microsoft.Web/serverfarms"
          }
        ],
        "id": "/subscriptions/3c974ab8-79df-42de-9811-da7b581583ef/resourceGroups/flyme-bis/providers/Microsoft.Web/sites/flyme-webapp",
        "resourceGroup": "flyme-bis",
        "resourceName": "flyme-webapp",
        "resourceType": "Microsoft.Web/sites"
      },
      {
        "dependsOn": [
          {
            "id": "/subscriptions/3c974ab8-79df-42de-9811-da7b581583ef/resourceGroups/flyme-bis/providers/Microsoft.Web/sites/flyme-webapp",
            "resourceGroup": "flyme-bis",
            "resourceName": "flyme-webapp",
            "resourceType": "Microsoft.Web/sites"
          }
        ],
        "id": "/subscriptions/3c974ab8-79df-42de-9811-da7b581583ef/resourceGroups/flyme-bis/providers/Microsoft.Web/sites/flyme-webapp/config/web",
        "resourceGroup": "flyme-bis",
        "resourceName": "flyme-webapp/web",
        "resourceType": "Microsoft.Web/sites/config"
      }
    ],
    "duration": "PT44.5379641S",
    "error": null,
    "mode": "Incremental",
    "onErrorDeployment": null,
    "outputResources": [
      {
        "id": "/subscriptions/3c974ab8-79df-42de-9811-da7b581583ef/resourceGroups/flyme-bis/providers/Microsoft.Web/serverfarms/flyme-plan",
        "resourceGroup": "flyme-bis"
      },
      {
        "id": "/subscriptions/3c974ab8-79df-42de-9811-da7b581583ef/resourceGroups/flyme-bis/providers/Microsoft.Web/sites/flyme-webapp",
        "resourceGroup": "flyme-bis"
      },
      {
        "id": "/subscriptions/3c974ab8-79df-42de-9811-da7b581583ef/resourceGroups/flyme-bis/providers/Microsoft.Web/sites/flyme-webapp/config/web",
        "resourceGroup": "flyme-bis"
      }
    ],
    "outputs": null,
    "parameters": {
      "appId": {
        "type": "String",
        "value": "0fb031ca-5e68-4ae1-969e-2e4d004b318f"
      },
      "appSecret": {
        "type": "String",
        "value": ""
      },
      "appServiceName": {
        "type": "String",
        "value": "flyme-webapp"
      },
      "existingAppServicePlanLocation": {
        "type": "String",
        "value": ""
      },
      "existingAppServicePlanName": {
        "type": "String",
        "value": ""
      },
      "newAppServicePlanLocation": {
        "type": "String",
        "value": "West Europe"
      },
      "newAppServicePlanName": {
        "type": "String",
        "value": "flyme-plan"
      },
      "newAppServicePlanSku": {
        "type": "Object",
        "value": {
          "capacity": 1,
          "family": "S",
          "name": "S1",
          "size": "S1",
          "tier": "Standard"
        }
      }
    },
    "parametersLink": null,
    "providers": [
      {
        "id": null,
        "namespace": "Microsoft.Web",
        "providerAuthorizationConsentState": null,
        "registrationPolicy": null,
        "registrationState": null,
        "resourceTypes": [
          {
            "aliases": null,
            "apiProfiles": null,
            "apiVersions": null,
            "capabilities": null,
            "defaultApiVersion": null,
            "locationMappings": null,
            "locations": [
              "westeurope"
            ],
            "properties": null,
            "resourceType": "serverfarms",
            "zoneMappings": null
          },
          {
            "aliases": null,
            "apiProfiles": null,
            "apiVersions": null,
            "capabilities": null,
            "defaultApiVersion": null,
            "locationMappings": null,
            "locations": [
              "westeurope"
            ],
            "properties": null,
            "resourceType": "sites",
            "zoneMappings": null
          },
          {
            "aliases": null,
            "apiProfiles": null,
            "apiVersions": null,
            "capabilities": null,
            "defaultApiVersion": null,
            "locationMappings": null,
            "locations": [
              "westeurope"
            ],
            "properties": null,
            "resourceType": "sites/config",
            "zoneMappings": null
          }
        ]
      }
    ],
    "provisioningState": "Succeeded",
    "templateHash": "3523345040284233625",
    "templateLink": null,
    "timestamp": "2023-01-17T20:46:46.405932+00:00",
    "validatedResources": null
  },
  "resourceGroup": "flyme-bis",
  "tags": null,
  "type": "Microsoft.Resources/deployments"
}

# create an Azure Bot
$ az deployment group create --resource-group "flyme-bis" --template-file 21.corebot-app-insights/deploymentTemplates/deployUseExistResourceGroup/template-AzureBot-with-rg.json --parameters 21.corebot-app-insights/deploymentTemplates/deployUseExistResourceGroup/parameters-for-template-AzureBot-with-rg.json
{
  "id": "/subscriptions/3c974ab8-79df-42de-9811-da7b581583ef/resourceGroups/flyme-bis/providers/Microsoft.Resources/deployments/template-AzureBot-with-rg",
  "location": null,
  "name": "template-AzureBot-with-rg",
  "properties": {
    "correlationId": "295aaf8e-fb00-4596-aa57-485065a21f12",
    "debugSetting": null,
    "dependencies": [],
    "duration": "PT9.667191S",
    "error": null,
    "mode": "Incremental",
    "onErrorDeployment": null,
    "outputResources": [
      {
        "id": "/subscriptions/3c974ab8-79df-42de-9811-da7b581583ef/resourceGroups/flyme-bis/providers/Microsoft.BotService/botServices/flyme-azurebot",
        "resourceGroup": "flyme-bis"
      }
    ],
    "outputs": null,
    "parameters": {
      "appId": {
        "type": "String",
        "value": "0fb031ca-5e68-4ae1-969e-2e4d004b318f"
      },
      "azureBotId": {
        "type": "String",
        "value": "flyme-azurebot"
      },
      "azureBotRegion": {
        "type": "String",
        "value": "global"
      },
      "azureBotSku": {
        "type": "String",
        "value": "S1"
      },
      "botEndpoint": {
        "type": "String",
        "value": "https://flyme-webapp.azurewebsites.net/api/messages"
      }
    },
    "parametersLink": null,
    "providers": [
      {
        "id": null,
        "namespace": "Microsoft.BotService",
        "providerAuthorizationConsentState": null,
        "registrationPolicy": null,
        "registrationState": null,
        "resourceTypes": [
          {
            "aliases": null,
            "apiProfiles": null,
            "apiVersions": null,
            "capabilities": null,
            "defaultApiVersion": null,
            "locationMappings": null,
            "locations": [
              "global"
            ],
            "properties": null,
            "resourceType": "botServices",
            "zoneMappings": null
          }
        ]
      }
    ],
    "provisioningState": "Succeeded",
    "templateHash": "7766259263394214844",
    "templateLink": null,
    "timestamp": "2023-01-17T21:02:10.661485+00:00",
    "validatedResources": null
  },
  "resourceGroup": "flyme-bis",
  "tags": null,
  "type": "Microsoft.Resources/deployments"
}

# publish bot to Azure
$ az webapp deployment source config-zip --resource-group flyme-bis --name flyme-webapp --src flyme-bot.zip 
Getting scm site credentials for zip deployment
Starting zip deployment. This operation can take a while to complete ...
Deployment endpoint responded with status code 202
Parameter persistence is turned on. Its information is saved in working directory /home/yo/Documents/OpenClassrooms/P10_chatbot. You can run `az config param-persist off` to turn it off.
Your preference of --resource-group: flyme-bis is now saved as persistent parameter. To learn more, type in `az config param-persist --help`
{
  "active": true,
  "author": "N/A",
  "author_email": "N/A",
  "build_summary": {
    "errors": [],
    "warnings": []
  },
  "complete": true,
  "deployer": "Push-Deployer",
  "end_time": "2023-01-17T21:36:27.2721733Z",
  "id": "c4ba632e-dcb7-407e-ace8-a5d57a41cf2d",
  "is_readonly": true,
  "is_temp": false,
  "last_success_end_time": "2023-01-17T21:36:27.2721733Z",
  "log_url": "https://flyme-webapp.scm.azurewebsites.net/api/deployments/latest/log",
  "message": "Created via a push deployment",
  "progress": "",
  "received_time": "2023-01-17T21:34:46.0270021Z",
  "site_name": "flyme-webapp",
  "start_time": "2023-01-17T21:34:47.4388155Z",
  "status": 4,
  "status_text": "",
  "url": "https://flyme-webapp.scm.azurewebsites.net/api/deployments/latest"
}
