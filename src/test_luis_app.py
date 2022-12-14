import json
import requests
import datetime
from pprint import pprint

from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient

from msrest.authentication import CognitiveServicesCredentials

SUBSCRIPTION_KEY_ENV_NAME = "8ad33ca9a5fb49589908dcede8f780b5"


def publish_app(client, app_id, version_id):
    publish_result = client.apps.publish(
        app_id,
        {
            'version_id': version_id,
            'is_staging': True,
            'region': 'westeurope'
        }
    )
    endpoint = publish_result.endpoint_url
    print("Your app is published. You can now go to test it on\n{}".format(endpoint))
    return endpoint



def test_luis_app(endpoint, pred_key, query):
    req_url = endpoint + \
        f"?verbose=true&show-all-intents=true&log=true" + \
        f"?subscription-key={pred_key}" + \
        f"&query={query}"

    pred = requests.get(req_url).json()
    print(json.dumps(pred, indent=4))


def management(subscription_key):
    """Managing
    This will show how to manage your LUIS applications.
    """
    client = LUISAuthoringClient(
        "https://flymeluisresource-authoring.cognitiveservices.azure.com/",
        CognitiveServicesCredentials(subscription_key),
    )

    try:
        # Create a LUIS app
        default_app_name = "Contoso-{}".format(datetime.datetime.now())
        version_id = "0.1"

        print("Creating App {}, version {}".format(
            default_app_name, version_id))

        app_id = client.apps.add({
            'name': default_app_name,
            'initial_version_id': version_id,
            'description': "New App created with LUIS Python sample",
            'culture': 'en-us',
        })
        print("Created app {}".format(app_id))

        # Listing app
        print("\nList all apps")
        for app in client.apps.list():
            print("\t->App: '{}'".format(app.name))

        # Cloning a version
        print("\nCloning version 0.1 into 0.2")
        client.versions.clone(
            app_id,
            "0.1",  # Source
            "0.2"   # New version name
        )
        print("Your app version has been cloned.")

        # Export the version
        print("\nExport version 0.2 as JSON")
        luis_app = client.versions.export(
            app_id,
            "0.2"
        )
        luis_app_as_json = json.dumps(luis_app.serialize())
        # You can now save this JSON string as a file

        # Import the version
        print("\nImport previously exported version as 0.3")
        luis_app
        client.versions.import_method(
            app_id,
            json.loads(luis_app_as_json),
            "0.3"
        )

        # Listing versions
        print("\nList all versions in this app")
        for version in client.versions.list(app_id):
            print("\t->Version: '{}', training status: {}".format(version.version,
                                                                  version.training_status))

        # Print app details
        print("\nPrint app '{}' details".format(default_app_name))
        details = client.apps.get(app_id)
        # as_dict "dictify" the object, by default it's attribute based. e.g. details.name
        pprint(details.as_dict())

        # Print version details
        print("\nPrint version '{}' details".format(version_id))
        details = client.versions.get(app_id, version_id)
        # as_dict "dictify" the object, by default it's attribute based. e.g. details.name
        pprint(details.as_dict())

        # Delete an app
        print("\nDelete app '{}'".format(default_app_name))
        client.apps.delete(app_id)
        print("App deleted!")

    except Exception as err:
        print("Encountered exception. {}".format(err))

if __name__ == '__main__':
    APP_ID = "1158aee4-d5f2-4e67-ba0b-323dff6fe6a2"
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