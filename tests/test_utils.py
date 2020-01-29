import json
from copy import deepcopy
from datetime import datetime, timedelta

from lumapps.api.utils import (
    list_prune_filters,
    _DiscoveryCacheDict,
    _DiscoveryCacheSqlite,
    DiscoveryCache,
    ConfigStore,
    _parse_endpoint_parts,
    _extract_from_discovery_spec,
    pop_matches,
)


def test_list_prune_filters(capsys):
    list_prune_filters()
    captured = capsys.readouterr()
    assert captured.out.startswith("PRUNE FILTERS:")


def test_discovery_cache_1():
    assert DiscoveryCache == _DiscoveryCacheSqlite


def test_discovery_cache_dict(mocker):
    mocker.patch("lumapps.api.utils.get_conf_db_file", return_value=":memory:")
    mocker.patch(
        "lumapps.api.utils.ConfigStore._get_conn", return_value=ConfigStore._get_conn()
    )
    c = _DiscoveryCacheDict
    assert c.get("foobar.com") is None
    c.set("foobar.com", "bla")
    assert c.get("foobar.com") == "bla"
    c._cache["foobar.com"]["expiry"] = datetime.now() - timedelta(days=100)
    assert c.get("foobar.com") is None


def test_discovery_cache_sqlite(mocker):
    mocker.patch("lumapps.api.utils.get_conf_db_file", return_value=":memory:")
    mocker.patch(
        "lumapps.api.utils.ConfigStore._get_conn", return_value=ConfigStore._get_conn()
    )
    c = _DiscoveryCacheSqlite
    assert c.get("foobar.com") is None
    c.set("foobar.com", "bla")
    assert c.get("foobar.com") == "bla"


def test_get_set_configs(mocker):
    mocker.patch("lumapps.api.utils.get_conf_db_file", return_value=":memory:")
    mocker.patch(
        "lumapps.api.utils.ConfigStore._get_conn", return_value=ConfigStore._get_conn()
    )
    assert len(ConfigStore.get_names()) == 0
    ConfigStore.set("foo", "bar")
    assert len(ConfigStore.get_names()) == 1
    ConfigStore.set("foo", "bar")
    assert len(ConfigStore.get_names()) == 1
    ConfigStore.set("foo1", "bar1")
    assert len(ConfigStore.get_names()) == 2
    assert ConfigStore.get("foo") == "bar"


def test_parse_endpoint_parts():
    s = ("user/get",)
    parts = _parse_endpoint_parts(s)
    assert parts == ["user", "get"]


def test_extract_from_discovery_spec():
    with open("tests/test_data/lumapps_discovery.json") as fh:
        discovery_doc = json.load(fh)
    name_parts = ["user", "get"]
    resources = discovery_doc["resources"]
    extracted = _extract_from_discovery_spec(resources, name_parts)

    assert extracted.get("httpMethod") == "GET"
    assert extracted.get("id") == "lumsites.user.get"


def test_pop_matches():
    d = {"a": 1, "b": {"c": 2, "d": {"e": 3}}, "z": 33}

    d2 = deepcopy(d)
    pth = "b/d/e"
    pop_matches(pth, d2)
    assert d2 == {"a": 1, "b": {"c": 2, "d": {}}, "z": 33}

    d2 = deepcopy(d)
    pth = "b"
    pop_matches(pth, d2)
    assert d2 == {"a": 1, "z": 33}

    d2 = deepcopy(d)
    pth = ""
    pop_matches(pth, d2)
    assert d2 == d

    s = "not a dict"
    pth = "foo/bar"
    pop_matches(pth, s)
    l1 = ["a", "b"]
    l2 = deepcopy(l1)
    pop_matches(pth, l1)
    assert l2 == l1

    obj = "foo"
    pop_matches("foo/bar", obj)
    assert obj == "foo"
