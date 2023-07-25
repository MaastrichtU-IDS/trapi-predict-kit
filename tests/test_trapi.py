import json
import os

from fastapi.testclient import TestClient

from trapi_predict_kit import TRAPI, settings

from .test_decorator import get_predictions

os.environ["VIRTUAL_HOST"] = "openpredict.semanticscience.org"
openapi_info = {
    "contact": {
        "name": "Firstname Lastname",
        "email": "email@example.com",
        # "x-id": "https://orcid.org/0000-0000-0000-0000",
        "x-role": "responsible developer",
    },
    "license": {
        "name": "MIT license",
        "url": "https://opensource.org/licenses/MIT",
    },
    "termsOfService": "https://github.com/your-org-or-username/my-model/blob/main/LICENSE.txt",
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

app = TRAPI(
    predict_endpoints=[get_predictions],
    info=openapi_info,
    title="OpenPredict TRAPI",
    version="1.0.0",
    openapi_version="3.0.1",
    description="""Machine learning models to produce predictions that can be integrated to Translator Reasoner APIs.
\n\nService supported by the [NCATS Translator project](https://ncats.nih.gov/translator/about)""",
    itrb_url_prefix="openpredict",
    dev_server_url="https://openpredict.semanticscience.org",
)
client = TestClient(app)


def test_get_predict_drug():
    """Test predict API GET operation for a drug"""
    url = "/predict?input_id=DRUGBANK:DB00394&n_results=42"
    response = client.get(url).json()
    assert len(response["hits"]) == 1
    assert response["count"] == 1
    assert response["hits"][0]["id"] == "drugbank:DB00001"


def test_get_meta_kg():
    """Get the metakg"""
    url = "/meta_knowledge_graph"
    response = client.get(url).json()
    assert len(response["edges"]) >= 1
    assert len(response["nodes"]) >= 1


def test_post_trapi():
    """Test Translator ReasonerAPI query POST operation to get predictions"""
    trapi_query = {
        "message": {
            "query_graph": {
                "edges": {"e01": {"subject": "n0", "object": "n1", "predicates": ["biolink:treats"]}},
                "nodes": {
                    "n0": {"categories": ["biolink:Drug"]},
                    "n1": {"ids": ["OMIM:246300"], "categories": ["biolink:Disease"]},
                },
            }
        },
        "query_options": {
            "n_results": 3,
            "min_score": 0,
            "max_score": 1,
        },
    }
    response = client.post(
        "/query",
        data=json.dumps(trapi_query),
        headers={"Content-Type": "application/json"},
    )
    # print(response.json())
    edges = response.json()["message"]["knowledge_graph"]["edges"].items()
    assert len(edges) == 1


def test_trapi_empty_response():
    trapi_query = {
        "message": {
            "query_graph": {
                "edges": {
                    "e00": {"subject": "n00", "object": "n01", "predicates": ["biolink:physically_interacts_with"]}
                },
                "nodes": {"n00": {"ids": ["CHEMBL.COMPOUND:CHEMBL112"]}, "n01": {"categories": ["biolink:Protein"]}},
            }
        }
    }
    response = client.post(
        "/query",
        data=json.dumps(trapi_query),
        headers={"Content-Type": "application/json"},
    )
    assert len(response.json()["message"]["results"]) == 0
