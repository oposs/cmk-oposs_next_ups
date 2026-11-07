"""The rule forms build, apply to the services, and prefill the check defaults."""

import importlib.util
import pathlib
import sys

import pytest
from cmk.rulesets.v1.form_specs import Dictionary, LevelDirection, SimpleLevels
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_next_ups"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def rule_specs():
    module = _load(PLUGIN / "rulesets/next_ups.py", "test_oposs_next_ups_rulesets")
    return {v.name: v for k, v in vars(module).items() if k.startswith("rule_spec_")}


@pytest.fixture(scope="module")
def check_plugins():
    module = _load(PLUGIN / "agent_based/oposs_next_ups.py", "test_oposs_next_ups_check_rs")
    return [v for k, v in vars(module).items() if k.startswith("check_plugin_")]


def test_every_rule_spec_is_check_parameters_for_itemless_services(rule_specs):
    assert rule_specs
    for spec in rule_specs.values():
        assert isinstance(spec, CheckParameters)
        # The services have no item, so the rule must not ask for one
        assert isinstance(spec.condition, HostCondition), spec.name


def test_every_check_ruleset_exists(rule_specs, check_plugins):
    used = {p.check_ruleset_name for p in check_plugins if p.check_ruleset_name}
    assert sorted(used - set(rule_specs)) == []


def test_every_rule_spec_is_used(rule_specs, check_plugins):
    used = {p.check_ruleset_name for p in check_plugins if p.check_ruleset_name}
    assert sorted(set(rule_specs) - used) == []


def test_forms_match_the_check_defaults(rule_specs, check_plugins):
    for plugin in check_plugins:
        if not plugin.check_ruleset_name:
            continue
        form = rule_specs[plugin.check_ruleset_name].parameter_form()
        assert isinstance(form, Dictionary)
        assert set(form.elements) == set(plugin.check_default_parameters), plugin.name
        for key, default in plugin.check_default_parameters.items():
            levels = form.elements[key].parameter_form
            assert isinstance(levels, SimpleLevels)
            direction = LevelDirection.UPPER if key == "levels_upper" else LevelDirection.LOWER
            assert levels.level_direction == direction, (plugin.name, key)
            assert default[0] == "fixed"
            assert levels.prefill_fixed_levels.value == default[1], (plugin.name, key)


def test_services_sharing_a_rule_share_the_defaults(check_plugins):
    by_rule = {}
    for plugin in check_plugins:
        if plugin.check_ruleset_name:
            by_rule.setdefault(plugin.check_ruleset_name, []).append(plugin.check_default_parameters)
    for name, defaults in by_rule.items():
        assert all(d == defaults[0] for d in defaults), name
