from trapi_predict_kit import resolve_entities


def test_resolve_entities():
    """Test the function to resolve entities using the Name Resolution API"""
    expect = 3
    resp = resolve_entities("alzheimer")
    assert len(resp) == expect
    assert "MONDO:0004975" in resp
