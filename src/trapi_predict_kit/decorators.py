import functools
from typing import Any, Callable, Dict, List, Optional

from reasoner_pydantic import MetaEdge, MetaNode

from trapi_predict_kit.types import PredictOptions


def trapi_predict(
    path: str,
    edges: List[MetaEdge],
    nodes: Dict[str, MetaNode],
    name: Optional[str] = None,
    description: Optional[str] = "",
    default_input: Optional[str] = "drugbank:DB00394",
    default_model: Optional[str] = "openpredict_baseline",
) -> Callable:
    """A decorator to indicate a function is a function to generate prediction that can be integrated to TRAPI.
    The function needs to take an input_id and returns a list of predicted entities related to the input entity
    """
    if not name:
        name = path

    def decorator(func: Callable) -> Any:
        @functools.wraps(func)
        def wrapper(input_id: str, options: Optional[PredictOptions] = None) -> Callable:
            options = PredictOptions.parse_obj(options) if options else PredictOptions()
            return func(input_id, options)

        wrapper._trapi_predict = {
            "edges": edges,
            "nodes": nodes,
            "path": path,
            "name": name,
            "description": description,
            "default_input": default_input,
            "default_model": default_model,
        }

        return wrapper

    return decorator
