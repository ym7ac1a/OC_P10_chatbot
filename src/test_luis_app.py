"""
Please, previously, make sure you have published the LUIS app via luis.ai
"""

import requests
import json


if __name__ == '__main__':
    APP_ID = "5e02b817-af9a-4335-892a-3b9acc444e45"
    AZURE_LUIS_PRED_ENDPOINT = \
        "https://flyme-luis-resource.cognitiveservices.azure.com/" + \
        f"luis/prediction/v3.0/apps/{APP_ID}/" + \
        "slots/staging/predict"
    AZURE_LUIS_PRED_KEY = "df63ca72a8894564a8bb8602771b30ad"

    query = "I want to book a trip from Paris to London for less than $100. " +\
        "I will leave on the first of January 2023 " + \
        "and come back on the 17th of january 2023."

    req_url = f"{AZURE_LUIS_PRED_ENDPOINT}" + \
        f"?verbose=true&show-all-intents=true&log=true" + \
        f"&subscription-key={AZURE_LUIS_PRED_KEY}" + \
        f"&query={query}"

    pred = requests.get(req_url).json()
    print(json.dumps(pred, indent=4))