"""Metric names: prefixed, declared, and translated from the legacy names."""

import importlib.util
import pathlib
import sys

import pytest
from cmk.agent_based.v2 import Metric
from cmk.graphing.v1 import graphs, metrics, perfometers, translations
from test_check import WALK, _fetch

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_next_ups"


def _load(path):
    name = "test_graphing_" + path.stem + "_" + path.parent.name
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def check():
    return _load(PLUGIN / "agent_based/oposs_next_ups.py")


@pytest.fixture(scope="module")
def graphing_objects():
    objects = []
    for path in sorted((PLUGIN / "graphing").glob("*.py")):
        objects.extend(vars(_load(path)).values())
    return objects


@pytest.fixture(scope="module")
def declared(graphing_objects):
    return {o.name for o in graphing_objects if isinstance(o, metrics.Metric)}


@pytest.fixture(scope="module")
def emitted(check):
    """check plugin name -> metric names it yields for the online UPS walk"""
    found = {}
    for key, plugin in vars(check).items():
        if not key.startswith("check_plugin_"):
            continue
        section_spec = vars(check)["snmp_section_" + plugin.name]
        section = section_spec.parse_function(_fetch(section_spec, WALK))
        if plugin.check_default_parameters is None:
            out = plugin.check_function(section)
        else:
            out = plugin.check_function(plugin.check_default_parameters, section)
        found[plugin.name] = [m.name for m in out if isinstance(m, Metric)]
    return found


@pytest.fixture(scope="module")
def translation_objects(graphing_objects):
    return [o for o in graphing_objects if isinstance(o, translations.Translation)]


def test_every_emitted_metric_is_prefixed(emitted):
    names = {n for ms in emitted.values() for n in ms}
    assert names
    assert sorted(n for n in names if not n.startswith("oposs_next_")) == []


def test_every_emitted_metric_is_declared(emitted, declared):
    names = {n for ms in emitted.values() for n in ms}
    assert sorted(names - declared) == []


def test_every_declared_metric_is_emitted(emitted, declared):
    names = {n for ms in emitted.values() for n in ms}
    assert sorted(declared - names) == []


def test_each_service_emits_at_most_one_metric(emitted):
    assert {name: ms for name, ms in emitted.items() if len(ms) > 1} == {}


def test_every_declared_name_is_prefixed(graphing_objects):
    kinds = (metrics.Metric, graphs.Graph, perfometers.Perfometer)
    names = [o.name for o in graphing_objects if isinstance(o, kinds)]
    assert names
    assert [n for n in names if not n.startswith("oposs_next_")] == []


def test_graphs_and_perfometers_use_declared_metrics(graphing_objects, declared):
    used = set()
    for o in graphing_objects:
        if isinstance(o, graphs.Graph):
            used.update(o.simple_lines)
        elif isinstance(o, perfometers.Perfometer):
            used.update(o.segments)
    assert used
    assert sorted(used - declared) == []


def test_translation_names_are_unique(translation_objects):
    names = [t.name for t in translation_objects]
    assert len(names) == len(set(names))


def test_translations_are_keyed_on_the_live_check_commands(translation_objects, emitted):
    # The lookup key is the check command a live service runs today; a key
    # naming a command that does not exist never fires.
    for t in translation_objects:
        assert t.check_commands == [translations.PassiveCheck(t.name)]
        assert t.name in emitted, t.name


def test_legacy_names_translate_to_the_metric_the_service_emits(translation_objects, emitted):
    for t in translation_objects:
        ((old, rule),) = t.translations.items()
        assert old in {"temperature", "voltage", "current", "frequency", "power",
                       "percentage", "duration"}
        assert isinstance(rule, translations.RenameTo)
        assert emitted[t.name] == [rule.metric_name], t.name


def test_every_service_with_a_metric_has_a_translation(translation_objects, emitted):
    with_metric = {name for name, ms in emitted.items() if ms}
    assert sorted(with_metric - {t.name for t in translation_objects}) == []
