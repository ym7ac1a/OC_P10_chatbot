import os
import time
from pathlib import Path
import json
import requests

import pandas as pd

from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import (
    ApplicationCreateObject,
    ExampleLabelObject,
    EntityLabelObject,
)

from msrest.authentication import CognitiveServicesCredentials
from tqdm import tqdm


def add_client_app(endpoint, key, project_name):
    # instanciate LUIS Authoring Client
    client = LUISAuthoringClient(
        endpoint, CognitiveServicesCredentials(key)
    )
    # define app basics
    appDefinition = ApplicationCreateObject(
        name=project_name,
        culture="en-us",
    )
    # create app
    app_id = client.apps.add(appDefinition)
    # get app id - necessary for all other changes
    print("Created LUIS app with ID {}".format(app_id))

    return client, app_id


def add_flyme_intents(client, app_id, version_id):
    book_id = client.model.add_intent(
        app_id=app_id, version_id=version_id, name="Book"
    )
    info_id = client.model.add_intent(
        app_id=app_id, version_id=version_id, name="Info"
    )


def add_flyme_prebuilts(client, app_id, version_id):
    client.model.add_prebuilt(
        app_id=app_id,
        version_id=version_id,
        prebuilt_extractor_names=["geographyV2"],
    )
    client.model.add_prebuilt(
        app_id=app_id,
        version_id=version_id,
        prebuilt_extractor_names=["datetimeV2"],
    )
    client.model.add_prebuilt(
        app_id=app_id,
        version_id=version_id,
        prebuilt_extractor_names=["number"],
    )


def add_flyme_feature_entity(
        client,
        app_id,
        version_id,
        entity_name,
        model_name,
):
    entity_id = client.model.add_entity(
        app_id=app_id, version_id=version_id, name=entity_name
    )
    client.features.add_entity_feature(
        app_id=app_id,
        version_id=version_id,
        entity_id=entity_id,
        feature_relation_create_object={
            "model_name": model_name,
        },
    )


def add_flyme_entities(
        client,
        app_id,
        version_id
):

    add_flyme_feature_entity(
        client,
        app_id,
        version_id,
        "or_city",
        "geographyV2")
    
    add_flyme_feature_entity(
        client,
        app_id,
        version_id,
        "dst_city",
        "geographyV2")
    
    add_flyme_feature_entity(
        client,
        app_id,
        version_id,
        "str_date",
        "datetimeV2")
    
    add_flyme_feature_entity(
        client,
        app_id,
        version_id,
        "end_date",
        "datetimeV2")
    
    add_flyme_feature_entity(
        client,
        app_id,
        version_id,
        "budget",
        "number")


def format_data_for_luis(
        json_path,
        batch_size,
        client,
        app_id,
        version_id
):
    raw_data = pd.read_json(json_path)

    entities = ["or_city", "dst_city", "str_date", "end_date", "budget"]
    examples = []
    unique_utterances = []

    for turn in tqdm(raw_data["turns"]):
        for frame in turn:
            if frame["author"] == "wizard" or frame["text"] in unique_utterances:
                continue

            unique_utterances.append(frame["text"])

            is_book = False
            labels = []

            for act in frame["labels"]["acts_without_refs"]:
                for arg in act["args"]:
                    if arg["key"] == "intent" and arg["val"] == "book":
                        is_book = True

                    if (
                        arg["key"] in entities
                        and arg["val"] is not None
                        and frame["text"].find(arg["val"]) != -1
                    ):
                        labels.append(
                            EntityLabelObject(
                                entity_name=arg["key"],
                                start_char_index=frame["text"].find(arg["val"]),
                                end_char_index=frame["text"].find(arg["val"])
                                + len(arg["val"]),
                            )
                        )

            if len(entities) > 0:
                examples.append(
                    ExampleLabelObject(
                        text=frame["text"],
                        intent_name="Book" if is_book else "Info",
                        entity_labels=labels,
                    )
                )

    # add the examples in batch
    for index in tqdm(range(0, len(examples), batch_size)):
        client.examples.batch(
            app_id=app_id,
            version_id=version_id,
            example_label_object_array=examples[index : index + batch_size],
        )


def train_flyme_data(client, app_id, version_id):
    client.train.train_version(app_id=app_id, version_id=version_id)
    waiting = True
    while waiting:
        info = client.train.get_status(app_id=app_id, version_id=version_id)

        # get_status returns a list of training statuses, one for each model. Loop through them and make sure all are done.
        waiting = any(
            map(
                lambda x: "Queued" == x.details.status or "InProgress" == x.details.status,
                info,
            )
        )
        if waiting:
            print("Waiting 10 seconds for training to complete...")
            time.sleep(10)
        else:
            print("trained")
            waiting = False


def publish_app(client, app_id, version_id):
    client.apps.update_settings(app_id, is_public=True)
    publish_result = client.apps.publish(
        app_id,
        version_id,
        is_staging=True,
        region='westeurope',
    )
    endpoint = publish_result.endpoint_url
    print(f"Your app is published. You can now go to test it on\n{endpoint}")


def test_luis_app(luis_endpoint, app_id, luis_key, query):
    pred_endpoint = f"{luis_endpoint}" + \
        f"luis/prediction/v3.0/apps/{app_id}/" + \
        "slots/staging/predict"

    req_url = f"{pred_endpoint}" + \
        f"?verbose=true&show-all-intents=true&log=true" + \
        f"&subscription-key={luis_key}" + \
        f"&query={query}"
    print(req_url)
    pred = requests.get(req_url).json()
    print(json.dumps(pred, indent=4))



def main():
    AZURE_LUIS_ENDPOINT = \
        "https://flymeluisresource-authoring.cognitiveservices.azure.com/"
    AZURE_LUIS_KEY = "8ad33ca9a5fb49589908dcede8f780b5"
    AZURE_LUIS_PROJECT_NAME = "flyme-luis-app-test"
    AZURE_LUIS_PROJECT_VERSION = "0.1"

    DATA_PATH = Path("./data")
    FRAMES_JSON_PATH = Path(DATA_PATH, "raw/frames.json")
    
    client, app_id = add_client_app(
        AZURE_LUIS_ENDPOINT, AZURE_LUIS_KEY, AZURE_LUIS_PROJECT_NAME)

    add_flyme_intents(client, app_id, AZURE_LUIS_PROJECT_VERSION)

    add_flyme_prebuilts(client, app_id, AZURE_LUIS_PROJECT_VERSION)

    add_flyme_entities(client, app_id, AZURE_LUIS_PROJECT_VERSION)

    format_data_for_luis(FRAMES_JSON_PATH, 100, client,
        app_id, AZURE_LUIS_PROJECT_VERSION)

    train_flyme_data(client, app_id, AZURE_LUIS_PROJECT_VERSION)
    
    publish_app(client, app_id, AZURE_LUIS_PROJECT_VERSION)
    
    query = "I want to book a trip from Paris to London for less than $100. " +\
        "I will leave on the first of January 2023 " + \
        "and come back on the 17th of january 2023."
    test_luis_app(AZURE_LUIS_ENDPOINT, "d008c5e2-b0c9-4c5d-92f6-262897bdc0ac", AZURE_LUIS_KEY, query)


if __name__== '__main__':
    main()
