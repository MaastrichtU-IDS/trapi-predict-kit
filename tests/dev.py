import logging
from typing import Optional

from trapi_predict_kit import TRAPI, PredictOptions, PredictOutput, trapi_predict
from trapi_predict_kit.config import settings

# Script to use to try the package in development

# Setup logger


log_level = logging.ERROR
if settings.DEV_MODE:
    log_level = logging.INFO
logging.basicConfig(level=log_level)


# Define additional metadata to integrate this function in TRAPI
@trapi_predict(
    path="/predict",
    name="Get predicted targets for a given entity",
    description="Return the predicted targets for a given entity: drug (DrugBank ID) or disease (OMIM ID), with confidence scores.",
    # Define which edges can be predicted by this function in a TRAPI query
    edges=[
        {
            "subject": "biolink:Drug",
            "predicate": "biolink:treats",
            "object": "biolink:Disease",
        },
        {
            "subject": "biolink:Disease",
            "predicate": "biolink:treated_by",
            "object": "biolink:Drug",
        },
    ],
    nodes={"biolink:Disease": {"id_prefixes": ["OMIM"]}, "biolink:Drug": {"id_prefixes": ["DRUGBANK"]}},
)
def get_predictions(input_id: str, options: Optional[PredictOptions] = None) -> PredictOutput:
    # You can easily load previously stored models
    # loaded_model = load("models/{{cookiecutter.module_name}}")
    # print(loaded_model.model)

    # Add the code to generate predicted associations for the provided input
    # loaded_model.model.predict_proba(x)

    # Predictions results should be a list of entities
    # for which there is a predicted association with the input entity
    predictions = {
        "hits": [
            {
                "id": "DB00001",
                "type": "biolink:Drug",
                "score": 0.12345,
                "label": "Leipirudin",
            }
        ],
        "count": 1,
    }
    return predictions


predict_endpoints = [get_predictions]

openapi_info = {
    "contact": {
        "name": "{{cookiecutter.author_name}}",
        "email": "{{cookiecutter.author_email}}",
        # "x-id": "{{cookiecutter.author_orcid}}",
        "x-role": "responsible developer",
    },
    "license": {
        "name": "MIT license",
        "url": "https://opensource.org/licenses/MIT",
    },
    "termsOfService": "https://github.com/{{cookiecutter.github_organization_name}}/{{cookiecutter.package_name}}/blob/main/LICENSE.txt",
    "x-translator": {
        "component": "KP",
        # TODO: update the Translator team to yours
        "team": ["Clinical Data Provider"],
        "biolink-version": settings.BIOLINK_VERSION,
        "infores": "infores:openpredict",
        "externalDocs": {
            "description": "The values for component and team are restricted according to this external JSON schema. See schema and examples at url",
            "url": "https://github.com/NCATSTranslator/translator_extensions/blob/production/x-translator/",
        },
    },
    "x-trapi": {
        "version": settings.TRAPI_VERSION,
        "asyncquery": False,
        "operations": [
            "lookup",
        ],
        "externalDocs": {
            "description": "The values for version are restricted according to the regex in this external JSON schema. See schema and examples at url",
            "url": "https://github.com/NCATSTranslator/translator_extensions/blob/production/x-trapi/",
        },
    },
}

servers = []
if settings.VIRTUAL_HOST:
    servers = [
        {
            "url": f"https://{settings.VIRTUAL_HOST}",
            "description": "TRAPI ITRB Production Server",
            "x-maturity": "production",
        },
    ]

app = TRAPI(
    predict_endpoints=predict_endpoints,
    servers=servers,
    info=openapi_info,
    title="TRAPI predict kit dev",
    version="1.0.0",
    openapi_version="3.0.1",
    description="""TRAPI predict kit development
\n\nService supported by the [NCATS Translator project](https://ncats.nih.gov/translator/about)""",
    dev_mode=True,
)


if __name__ == "__main__":
    # To be run when the script is executed directly
    input_id = "drugbank:DB00002"
    # if len(sys.argv) > 0:
    #     input_id = sys.argv[1]
    print(get_predictions(input_id, PredictOptions()))
