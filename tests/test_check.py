"""Tests for the NextUPS SNMP check plugins (run on the Checkmk server).

There is no captured walk of a real device in the repository. The data below
is built from the MIBs the plugin reads, with the units the MIBs state:

- UPS-MIB (RFC 1628), base .1.3.6.1.2.1.33.1
- NextUPSSystems MIB, base .1.3.6.1.4.1.21111.1.1 (oidref.com, circitor.fr)

A section is filled the way Checkmk fills it: every walk entry at or below
`fetch.base + "." + column` becomes one row.
"""

import importlib.util
import json
import math
import pathlib
import re
import sys

import pytest
from cmk.agent_based.v2 import Metric, Result, Service, State

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECK = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_next_ups/agent_based/oposs_next_ups.py"

UPS = ".1.3.6.1.2.1.33.1"
NEXT = ".1.3.6.1.4.1.21111.1.1"
PHASES = ("RS", "ST", "TR")

# The plugin reads the phase rows with the indexes 0, 1 and 2, so the walk
# uses them too. See test_phase_columns_match_the_mib for the MIB side.
INDEX = {"RS": 0, "ST": 1, "TR": 2}

# A three-phase UPS on mains, battery full.
WALK = {
    NEXT + ".1.3.0": "WPHVR3K0",               # upsIdModelName
    UPS + ".6.1.0": "0",                        # upsAlarmsPresent
    NEXT + ".3.1.0": "2",                       # upsBatStatus: batteryNormal
    NEXT + ".3.13.0": "253",                    # upsBatTemperature, 0.1 degC
    UPS + ".2.2.0": "0",                        # upsSecondsOnBattery, s
    UPS + ".2.3.0": "45",                       # upsEstimatedMinutesRemaining, min
    UPS + ".2.4.0": "100",                      # upsEstimatedChargeRemaining, %
    UPS + ".2.5.0": "2720",                     # upsBatteryVoltage, 0.1 V DC
    UPS + ".2.6.0": "0",                        # upsBatteryCurrent, 0.1 A DC
}
for _i in INDEX.values():
    WALK.update({
        f"{NEXT}.4.5.1.2.{_i}": "500",          # upsInFrequency, 0.1 Hz
        f"{NEXT}.4.5.1.3.{_i}": "2301",         # upsInVoltage, 0.1 V
        f"{NEXT}.4.5.1.4.{_i}": "52",           # upsInCurrent, 0.1 A
        f"{NEXT}.5.7.1.2.{_i}": "2300",         # upsOutVoltage, 0.1 V
        f"{NEXT}.5.7.1.3.{_i}": "41",           # upsOutCurrent, 0.1 A
        f"{NEXT}.5.7.1.4.{_i}": "9500",         # upsOutApparentPower, 0.1 VA
        f"{NEXT}.5.7.1.5.{_i}": "8800",         # upsOutTruePower, 0.1 W
        f"{NEXT}.5.7.1.6.{_i}": "93",           # upsOutPowerFactor, 0.01
        f"{NEXT}.5.7.1.7.{_i}": "23",           # upsOutPercentLoad, %
        f"{NEXT}.5.7.1.8.{_i}": "3984",         # upsOutLineVoltage, 0.1 V
        f"{NEXT}.5.7.1.9.{_i}": "500",          # upsOutFrequency, 0.1 Hz
        f"{NEXT}.6.3.1.2.{_i}": "2302",         # upsByVoltage, 0.1 V
        f"{NEXT}.6.3.1.3.{_i}": "0",            # upsByCurrent, 0.1 A
        f"{NEXT}.6.3.1.4.{_i}": "0",            # upsByPower, 0.1 W
        f"{NEXT}.6.3.1.5.{_i}": "3986",         # upsByLineVoltage, 0.1 V
    })

# The MIB object each service is meant to read: (OID column, factor that
# turns the raw MIB value into the base unit the metric is declared in).
PER_PHASE_MIB = {
    "Input Frequency": (NEXT + ".4.5.1.2", 0.1),       # Hz
    "Input Voltage": (NEXT + ".4.5.1.3", 0.1),         # V
    "Input Current": (NEXT + ".4.5.1.4", 0.1),         # A
    "Output Voltage": (NEXT + ".5.7.1.2", 0.1),        # V
    "Output Current": (NEXT + ".5.7.1.3", 0.1),        # A
    "Output Apparent Power": (NEXT + ".5.7.1.4", 0.1),  # VA
    "Output True Power": (NEXT + ".5.7.1.5", 0.1),     # W
    "Output Load": (NEXT + ".5.7.1.7", 1.0),           # %
    "Output Frequency": (NEXT + ".5.7.1.9", 0.1),      # Hz
    "Bypass Voltage": (NEXT + ".6.3.1.2", 0.1),        # V
    "Bypass Current": (NEXT + ".6.3.1.3", 0.1),        # A
    "Bypass True Power": (NEXT + ".6.3.1.4", 0.1),     # W
}
SCALAR_MIB = {
    "UPS Alarm Check": UPS + ".6.1",
    "Battery State": NEXT + ".3.1",
    "Battery Temperature": NEXT + ".3.13",
    "Time On Battery": UPS + ".2.2",
    "Battery Time Remaining": UPS + ".2.3",
    "Battery Charge Remaining": UPS + ".2.4",
    "Battery Voltage": UPS + ".2.5",
    "Battery Current": UPS + ".2.6",
}
SERVICES = sorted(
    [f"Phase {p} {kind}" for p in PHASES for kind in PER_PHASE_MIB] + list(SCALAR_MIB)
)


@pytest.fixture(scope="module")
def check():
    name = "test_oposs_next_ups_check"
    spec = importlib.util.spec_from_file_location(name, CHECK)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    yield module
    sys.modules.pop(name, None)


@pytest.fixture(scope="module")
def plugins(check):
    """service name -> (snmp section, check plugin)"""
    found = {}
    for key, plugin in vars(check).items():
        if key.startswith("check_plugin_"):
            section = vars(check)["snmp_section_" + plugin.name]
            found[plugin.service_name] = (section, plugin)
    return found


def _fetch(section, walk):
    """The string table Checkmk hands the parse function: one table per tree."""
    tables = []
    for tree in section.fetch:
        rows = []
        for column in tree.oids:
            oid = f"{tree.base}.{column.column}"
            rows.extend([value] for key, value in sorted(walk.items())
                        if key == oid or key.startswith(oid + "."))
        tables.append(rows)
    return tables


def _run(plugins, service, walk=None, params=None, **override):
    """Parse, discover and check one service; `override` maps OID -> raw value."""
    walk = dict(WALK if walk is None else walk)
    walk.update(override)
    section_spec, plugin = plugins[service]
    section = section_spec.parse_function(_fetch(section_spec, walk))
    discovered = list(plugin.discovery_function(section))
    if plugin.check_default_parameters is None:
        out = list(plugin.check_function(section))
    else:
        merged = dict(plugin.check_default_parameters)
        merged.update(params or {})
        out = list(plugin.check_function(merged, section))
    return discovered, out


def _oid(plugins, service):
    """The full OID the plugin fetches for this service."""
    section, _plugin = plugins[service]
    (tree,) = section.fetch
    (column,) = tree.oids
    return f"{tree.base}.{column.column}"


def _results(out):
    return [o for o in out if isinstance(o, Result)]


def _metrics(out):
    return {o.name: o.value for o in out if isinstance(o, Metric)}


# ---------------------------------------------------------------------------
# Inventory and detection
# ---------------------------------------------------------------------------

def test_every_service_has_a_plugin(plugins):
    assert sorted(plugins) == SERVICES
    assert len(plugins) == 44


def test_plugin_names_follow_the_service_names(plugins):
    for service, (section, plugin) in plugins.items():
        assert plugin.name == "oposs_next_ups_" + service.lower().replace(" ", "_")
        assert [str(s) for s in plugin.sections] == [plugin.name]
        assert str(section.name) == plugin.name


def _detects(spec, oids):
    return any(
        all(bool(re.fullmatch(regex, oids.get(oid, ""), re.DOTALL)) is wanted
            for oid, regex, wanted in clause)
        for clause in spec
    )


@pytest.mark.parametrize("model, expected", [
    ("WPHVR3K0", True),
    ("WPHVR3K0XL", True),
    ("Smart-UPS 3000", False),
    ("", False),
])
def test_detection_on_the_model_name(plugins, model, expected):
    # upsIdModelName of the NextUPS MIB
    for section, _plugin in plugins.values():
        assert _detects(section.detect, {NEXT + ".1.3.0": model}) is expected


# ---------------------------------------------------------------------------
# The OIDs and scales the MIBs define
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("service", sorted(SCALAR_MIB))
def test_scalar_oids_match_the_mib(plugins, service):
    # Walking the object or its .0 instance returns the same single row
    assert _oid(plugins, service) in (SCALAR_MIB[service], SCALAR_MIB[service] + ".0")


PHASE_CASES = [
    pytest.param(phase, kind, marks=pytest.mark.xfail(
        strict=True, raises=AssertionError,
        reason="BUG: Bypass True Power reads .6.3.1.5 upsByLineVoltage, not .6.3.1.4 upsByPower"))
    if kind == "Bypass True Power" else (phase, kind)
    for phase in PHASES for kind in sorted(PER_PHASE_MIB)
]


@pytest.mark.parametrize("phase, kind", PHASE_CASES)
def test_phase_columns_match_the_mib(plugins, phase, kind):
    # The MIB text of upsOutLineVoltage/upsByLineVoltage names index 1 as
    # the RS phase; the plugin uses 0, 1, 2. Without a walk of a real
    # device this test only pins the column, and the index the plugin uses.
    column, _factor = PER_PHASE_MIB[kind]
    assert _oid(plugins, f"Phase {phase} {kind}") == f"{column}.{INDEX[phase]}"


def _metric_value(plugins, service, raw):
    _disc, out = _run(plugins, service, **{_oid(plugins, service): raw})
    (value,) = _metrics(out).values()
    return value


SCALE_CASES = [
    pytest.param(kind, marks=pytest.mark.xfail(
        strict=True, raises=AssertionError,
        reason="BUG: Output Apparent/True Power scale the 0.1 VA / 0.1 W MIB value by 100, 1000x too high"))
    if kind in ("Output Apparent Power", "Output True Power") else kind
    for kind in sorted(set(PER_PHASE_MIB) - {"Bypass True Power"})
]


@pytest.mark.parametrize("kind", SCALE_CASES)
def test_phase_values_are_scaled_as_the_mib_says(plugins, kind):
    _column, factor = PER_PHASE_MIB[kind]
    assert _metric_value(plugins, f"Phase RS {kind}", "1234") == pytest.approx(1234 * factor)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="BUG: Bypass True Power shows the bypass line voltage times 100 as watts")
def test_bypass_true_power_reports_the_bypass_power(plugins):
    # Bypass idle: upsByPower 0, upsByLineVoltage 398.6 V
    _disc, out = _run(plugins, "Phase RS Bypass True Power")
    assert _metrics(out) == {"oposs_next_true_power": 0.0}


@pytest.mark.parametrize("service, raw, metric, value", [
    ("Battery Temperature", "253", "oposs_next_temperature", 25.3),
    ("Battery Voltage", "2720", "oposs_next_voltage", 272.0),
    ("Battery Current", "-125", "oposs_next_current", -12.5),  # Integer32, discharging
    ("Battery Charge Remaining", "87", "oposs_next_battery_pct", 87.0),
    ("Battery Time Remaining", "45", "oposs_next_time_remaining", 2700.0),  # minutes -> s
    ("Time On Battery", "95", "oposs_next_time_on_battery", 95.0),
])
def test_scalar_values_are_scaled_as_the_mib_says(plugins, service, raw, metric, value):
    _disc, out = _run(plugins, service, **{_oid(plugins, service): raw})
    assert _metrics(out) == {metric: pytest.approx(value)}


# ---------------------------------------------------------------------------
# A healthy UPS
# ---------------------------------------------------------------------------

def test_online_ups_discovers_every_service(plugins):
    for service in SERVICES:
        discovered, _out = _run(plugins, service)
        assert discovered == [Service()], service


def test_online_ups_is_ok_everywhere(plugins):
    for service in SERVICES:
        _disc, out = _run(plugins, service)
        states = [r.state for r in _results(out)]
        assert states == [State.OK], (service, out)


@pytest.mark.parametrize("service, summary", [
    ("UPS Alarm Check", "No Alarms"),
    ("Battery State", "Battery Normal"),
    ("Battery Temperature", "Battery Temperature: 25 °C"),
    ("Battery Voltage", "Battery Voltage: 272.0 V"),
    ("Battery Charge Remaining", "Battery Charge Remaining: 100 %"),
    ("Battery Time Remaining", "Battery Time Remaining: 45 minutes 0 seconds"),
    ("Phase RS Input Voltage", "Phase RS Input Voltage: 230 V"),
    ("Phase RS Input Frequency", "Phase RS Input Frequency: 50.00 Hz"),
    ("Phase ST Output Load", "Phase ST Output Load: 23 %"),
    ("Phase TR Output Current", "Phase TR Output Current: 4 A"),
])
def test_online_ups_summaries(plugins, service, summary):
    _disc, out = _run(plugins, service)
    assert [r.summary for r in _results(out)] == [summary]


@pytest.mark.parametrize("service, metric", [
    ("Battery Temperature", "oposs_next_temperature"),
    ("Phase RS Input Voltage", "oposs_next_voltage"),
    ("Phase RS Output Frequency", "oposs_next_frequency"),
    ("Phase RS Bypass Current", "oposs_next_current"),
    ("Phase RS Output Apparent Power", "oposs_next_apparent_power"),
    ("Phase RS Output True Power", "oposs_next_true_power"),
    ("Phase RS Output Load", "oposs_next_load_pct"),
    ("Battery Charge Remaining", "oposs_next_battery_pct"),
    ("Battery Time Remaining", "oposs_next_time_remaining"),
    ("Time On Battery", "oposs_next_time_on_battery"),
])
def test_metric_names(plugins, service, metric):
    _disc, out = _run(plugins, service)
    assert list(_metrics(out)) == [metric]


def test_state_services_emit_no_metrics(plugins):
    for service in ("UPS Alarm Check", "Battery State"):
        _disc, out = _run(plugins, service)
        assert _metrics(out) == {}


# ---------------------------------------------------------------------------
# State mapping services
# ---------------------------------------------------------------------------

def test_alarms_present_is_crit(plugins):
    _disc, out = _run(plugins, "UPS Alarm Check", **{UPS + ".6.1.0": "2"})
    assert _results(out) == [Result(state=State.CRIT, summary="2 Alarms present - check online status!")]


@pytest.mark.parametrize("raw, state, summary", [
    ("0", State.UNKNOWN, "UNKNOWN state"),
    ("1", State.CRIT, "UNKNOWN state"),          # MIB: unknown(1)
    ("2", State.OK, "Battery Normal"),
    ("3", State.WARN, "Battery Low"),
    ("4", State.CRIT, "Battery Depleted"),
    ("5", State.WARN, "Battery Discharging"),
    ("6", State.CRIT, "Battery Failure"),
    ("7", State.CRIT, "Battery Replace"),
    ("8", State.CRIT, "Battery Silence"),
    ("9", State.CRIT, "unknown(9)"),
])
def test_battery_state(plugins, raw, state, summary):
    _disc, out = _run(plugins, "Battery State", **{NEXT + ".3.1.0": raw})
    assert _results(out) == [Result(state=state, summary=summary)]


# ---------------------------------------------------------------------------
# Threshold paths of the default levels
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("service, raw, state", [
    ("Battery Temperature", "599", State.OK),
    ("Battery Temperature", "600", State.WARN),
    ("Battery Temperature", "700", State.CRIT),
    ("Phase RS Input Voltage", "2100", State.OK),
    ("Phase RS Input Voltage", "2099", State.WARN),
    ("Phase RS Input Voltage", "1799", State.CRIT),
    ("Phase ST Output Voltage", "2050", State.WARN),
    ("Phase TR Bypass Voltage", "1500", State.CRIT),
    ("Phase RS Input Frequency", "489", State.WARN),
    ("Phase RS Input Frequency", "479", State.CRIT),
    ("Phase RS Input Frequency", "510", State.WARN),
    ("Phase RS Input Frequency", "520", State.CRIT),
    ("Phase ST Output Frequency", "515", State.WARN),
    ("Phase ST Output Frequency", "470", State.CRIT),
    ("Phase RS Output Load", "79", State.OK),
    ("Phase RS Output Load", "80", State.WARN),
    ("Phase RS Output Load", "90", State.CRIT),
    ("Battery Charge Remaining", "15", State.OK),
    ("Battery Charge Remaining", "14", State.WARN),
    ("Battery Charge Remaining", "9", State.CRIT),
    ("Battery Time Remaining", "20", State.OK),      # 1200 s
    ("Battery Time Remaining", "19", State.WARN),
    ("Battery Time Remaining", "9", State.CRIT),
    ("Time On Battery", "59", State.OK),
    ("Time On Battery", "60", State.WARN),
    ("Time On Battery", "300", State.CRIT),
])
def test_default_levels(plugins, service, raw, state):
    _disc, out = _run(plugins, service, **{_oid(plugins, service): raw})
    assert [r.state for r in _results(out)] == [state]


def test_rule_levels_replace_the_defaults(plugins):
    params = {"levels_upper": ("fixed", (30.0, 40.0))}
    _disc, out = _run(plugins, "Battery Temperature", params=params, **{NEXT + ".3.13.0": "350"})
    assert [r.state for r in _results(out)] == [State.WARN]


def test_levels_switched_off_keep_the_service_ok(plugins):
    params = {"levels_lower": ("no_levels", None)}
    _disc, out = _run(plugins, "Battery Charge Remaining", params=params, **{UPS + ".2.4.0": "1"})
    assert [r.state for r in _results(out)] == [State.OK]
    assert _metrics(out) == {"oposs_next_battery_pct": 1.0}


@pytest.mark.parametrize("service", [s for s in SERVICES if "Current" in s or "Power" in s
                                     or s in ("Battery Voltage",)])
def test_info_only_services_have_no_levels(plugins, service):
    _section, plugin = plugins[service]
    assert plugin.check_default_parameters == {}
    assert plugin.check_ruleset_name is None
    _disc, out = _run(plugins, service, **{_oid(plugins, service): "999999"})
    assert [r.state for r in _results(out)] == [State.OK]


# ---------------------------------------------------------------------------
# No input on a phase: frequency 0
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("service", ["Phase RS Input Frequency", "Phase TR Output Frequency"])
def test_zero_frequency_is_not_a_level_violation(plugins, service):
    # skip_zero: a phase without input reads 0 Hz, which would otherwise be CRIT
    _disc, out = _run(plugins, service, **{_oid(plugins, service): "0"})
    assert [r.state for r in _results(out)] == [State.OK]
    (value,) = _metrics(out).values()
    assert math.isnan(value)


def test_zero_voltage_is_crit(plugins):
    # Only frequencies are skipped; a dead phase still alarms on its voltage
    _disc, out = _run(plugins, "Phase RS Input Voltage", **{NEXT + ".4.5.1.3.0": "0"})
    assert [r.state for r in _results(out)] == [State.CRIT]


# ---------------------------------------------------------------------------
# Missing and broken data
# ---------------------------------------------------------------------------

def test_a_ups_without_a_value_gets_no_service(plugins):
    for service in SERVICES:
        walk = {k: v for k, v in WALK.items() if not k.startswith(_oid(plugins, service))}
        discovered, out = _run(plugins, service, walk=walk)
        assert discovered == [], service
        assert out == [], service


def test_a_single_phase_ups_gets_only_the_rs_services(plugins):
    walk = {k: v for k, v in WALK.items() if not re.search(r"\.(4\.5|5\.7|6\.3)\.1\.\d+\.[12]$", k)}
    for service in SERVICES:
        discovered, _out = _run(plugins, service, walk=walk)
        expected = [] if service.startswith(("Phase ST", "Phase TR")) else [Service()]
        assert discovered == expected, service


@pytest.mark.parametrize("raw", ["", "NULL"])
@pytest.mark.parametrize("service", ["Battery Temperature", "Phase RS Input Frequency", "Battery Current"])
def test_a_non_numeric_value_is_unknown(plugins, service, raw):
    _disc, out = _run(plugins, service, **{_oid(plugins, service): raw})
    assert out == [Result(state=State.UNKNOWN, summary=f"{service}: the UPS sent no number ({raw!r})")]


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw, summary", [
    ("0", "Time On Battery: 0 seconds"),
    ("45", "Time On Battery: 45 seconds"),
    ("120", "Time On Battery: 2 minutes 0 seconds (warn/crit at 1 minute 0 seconds/5 minutes 0 seconds)"),
    ("3725", "Time On Battery: 1 hour 2 minutes (warn/crit at 1 minute 0 seconds/5 minutes 0 seconds)"),
])
def test_time_on_battery_shows_minutes(plugins, raw, summary):
    _disc, out = _run(plugins, "Time On Battery", **{UPS + ".2.2.0": raw})
    assert [r.summary for r in _results(out)] == [summary]


@pytest.mark.parametrize("raw, summary", [
    # upsEstimatedMinutesRemaining is in minutes on the wire
    ("45", "Battery Time Remaining: 45 minutes 0 seconds"),
    ("20", "Battery Time Remaining: 20 minutes 0 seconds"),
    ("19", "Battery Time Remaining: 19 minutes 0 seconds (warn/crit below 20 minutes 0 seconds/10 minutes 0 seconds)"),
    ("90", "Battery Time Remaining: 1 hour 30 minutes"),
])
def test_battery_time_remaining_shows_minutes(plugins, raw, summary):
    _disc, out = _run(plugins, "Battery Time Remaining", **{UPS + ".2.3.0": raw})
    assert [r.summary for r in _results(out)] == [summary]
    assert _metrics(out) == {"oposs_next_time_remaining": int(raw) * 60.0}


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

def test_check_carries_the_released_version():
    # The publish check fails on main when a version file disagrees with
    # the newest released CHANGES.md heading.
    released = re.search(r"^## (\d+\.\d+\.\d+)", (ROOT / "CHANGES.md").read_text(),
                         flags=re.MULTILINE).group(1)
    assert re.search(rf'^__version__ = "{re.escape(released)}"$', CHECK.read_text(), flags=re.MULTILINE)


def test_release_writes_version_into_check(tmp_path):
    """Apply the version_files entry of .github/repo-infra.json to the check
    module, as Create release PR does (a multiline regex, first match)"""
    config = json.loads((ROOT / ".github/repo-infra.json").read_text())
    (spec,) = [f for f in config["version_files"] if (ROOT / f["path"]) == CHECK]
    stamped = re.sub(spec["pattern"], spec["replacement"].replace("$VERSION", "9.8.7"),
                     CHECK.read_text(), count=1, flags=re.MULTILINE)
    assert re.search(spec["verify"].replace("$VERSION", re.escape("9.8.7")), stamped, flags=re.MULTILINE)
    copy = tmp_path / "stamped_check.py"
    copy.write_text(stamped)
    module_spec = importlib.util.spec_from_file_location("stamped_check", copy)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    assert module.__version__ == "9.8.7"
