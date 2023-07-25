import json

from fastapi.testclient import TestClient

from .conftest import app

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


def test_healthcheck():
    response = client.get("/health")
    assert response.json() == {"status": "ok"}


def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
