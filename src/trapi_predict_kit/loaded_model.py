import pickle
from dataclasses import dataclass
from typing import Any, Optional

from mlem import api as mlem
from rdflib import Graph

# from mlem.api import save as mlem_save, load as mlem_load
from trapi_predict_kit.rdf_utils import get_run_metadata
from trapi_predict_kit.utils import log


@dataclass
class LoadedModel:
    path: str
    model: Any
    metadata: Graph
    hyper_params: Optional[Any] = None
    scores: Optional[Any] = None
    # features: Any = None


def save(
    model: Any,
    path: str,
    sample_data: Any,
    method: str = "pickle",
    scores: Optional[Any] = None,
    hyper_params: Optional[Any] = None,
    # model: Any,
    # path: str,
    # sample_data: Any,
    # scores: Optional[Dict] = None,
    # hyper_params: Optional[Dict] = None,
) -> LoadedModel:
    model_name = path.rsplit("/", 1)[-1]
    # print(os.path.isabs(path))
    # if not os.path.isabs(path):
    #     path = os.path.join(os.getcwd(), path)
    log.info(f"💾 Saving the model in {path} using {method}")

    # mlem_model = MlemModel.from_obj(model, sample_data=sample_data)
    # mlem_model.dump(path)
    # print(mlem_model)
    if method == "mlem":
        mlem.save(model, path, sample_data=sample_data)
    else:
        with open(path, "wb") as f:
            pickle.dump(model, f)

    g = get_run_metadata(scores, sample_data, hyper_params, model_name)
    g.serialize(f"{path}.ttl", format="ttl")
    # os.chmod(f"{path}.ttl", 0o644)
    # os.chmod(f"{path}.mlem", 0o644)

    return LoadedModel(
        path=path,
        model=model,
        metadata=g,
        hyper_params=hyper_params,
        scores=scores,
    )


def load(path: str, method: str = "pickle") -> LoadedModel:
    log.info(f"💽 Loading model from {path} using {method}")
    if method == "mlem":
        model = mlem.load(path)
    else:
        with open(path, "rb") as f:
            model = pickle.load(f)

    g = Graph()
    g.parse(f"{path}.ttl", format="ttl")
    # TODO: extract scores and hyper_params from RDF?

    return LoadedModel(path=path, model=model, metadata=g)
