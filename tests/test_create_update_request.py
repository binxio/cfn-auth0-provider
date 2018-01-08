from request_update import create_update_request, get_property_value_by_path, remove_property_by_path


def test_get_property():
    request = {"identifier": "abc"}
    v = get_property_value_by_path(request, "identifier")
    assert v == "abc"

    v = get_property_value_by_path(request, "identixfier")
    assert v is None


def test_nested_get_properties():
    request = {"jwt": {"iss": "bla", "secret_encoded": True}}

    v = get_property_value_by_path(request, "jwt.secret_encoded")
    assert isinstance(v, bool) and v
    assert "jwt" in request
    assert "iss" in request["jwt"]

    v = get_property_value_by_path(request, "jwt.secret_encoded.more")
    assert v is None


def test_remove_property():
    request = {"identifier": "abc"}
    remove_property_by_path(request, "identifier")
    assert "identifier" not in request

    request = {"abc": "identifier"}
    remove_property_by_path(request, "identifier")
    assert "abc" in request


def test_remove_nested_property():
    request = {"jwt": {"iss": "bla", "secret_encoded": True}}

    remove_property_by_path(request, "jwt.secret_encoded")
    assert "jwt" in request
    assert "secret_encoded" not in request["jwt"]
    assert "iss" in request["jwt"]

    remove_property_by_path(request, "jwt.secret_encoded")
    assert "jwt" in request
    assert "secret_encoded" not in request["jwt"]
    assert "iss" in request["jwt"]


def test_create_update_request():
    r = create_update_request("Custom::Auth0ResourceServer", {"identifier": "abc"}, {"abc": "x", "identifier": "abc"})
    assert "abc" in r
    assert "identifier" not in r

    r = create_update_request("Custom::Auth0ResourceServer", {}, {"abc": "x", "identifier": "abc"})
    assert "abc" in r
    assert "identifier" not in r

    r = create_update_request("Custom::Auth0ResourceServer", {"identifier": "ABC"}, {"abc": "x", "identifier": "abc"})
    assert "identifier" in r
