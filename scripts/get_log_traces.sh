#!/bin/bash

# Authentification
echo "Login and Authenticate..."
az login --output none
az account set \
     --subscription "OCR - Microsoft Azure" \
     --output none

# get negative traces for the last 24 hours, will be used to improve Luis application
echo $(az monitor app-insights query -a luis-app-ins \
                               --resource-group flymebot2101 \
                               --analytics-query "traces" \
                               --offset 5d) | jq '.' > trace_logs.json

python treat_neg_traces.py
