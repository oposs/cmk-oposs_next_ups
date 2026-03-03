#!/usr/bin/env python3

from collections import namedtuple

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    check_levels,
    startswith,
)

# SNMP OID bases
upsMIB = ".1.3.6.1.2.1.33.1"  # https://www.circitor.fr/Mibs/Html/U/UPS-MIB.php
nextUpsMIB = ".1.3.6.1.4.1.21111.1.1"  # https://www.circitor.fr/Mibs/Html/N/NextUPSSystems.php

# SNMP detection: NextUPS / Winner Pro / Voltronic
DETECT_NEXT_UPS = startswith(".1.3.6.1.4.1.21111.1.1.1.3.0", "WPHVR3K0")

BATTERY_STATE_MAP = {
    "0": "UNKNOWN state",
    "1": "UNKNOWN state",
    "2": "Battery Normal",
    "3": "Battery Low",
    "4": "Battery Depleted",
    "5": "Battery Discharging",
    "6": "Battery Failure",
    "7": "Battery Replace",
    "8": "Battery Silence",
}

# ---------------------------------------------------------------------------
# Target definitions — each entry generates one SimpleSNMPSection + CheckPlugin
#
# Two patterns:
#   'result' key  -> state-mapping check (no params, no levels)
#   otherwise     -> check_levels check (with params, configurable thresholds)
#
# For check_levels targets:
#   scale         — multiply raw SNMP int by this factor
#   skip_zero     — when True, emit NaN instead of 0 (frequency w/o input)
#   metric_name   — prefixed metric name for perfdata
#   render_func   — display formatter
#   default_params — SimpleLevels format: {"levels_upper": ("fixed", (w,c))}
#   boundaries    — graph boundaries tuple
#   ruleset_name  — shared WATO ruleset name (optional)
# ---------------------------------------------------------------------------

targets = [
    # --- Alarm ---
    {
        "name": "UPS Alarm Check",
        "query": SNMPTree(base=upsMIB + ".6", oids=["1"]),
        "keys": ["upsAlarmPresent"],
        "result": lambda obj, cfg: Result(
            state=State.OK if obj.upsAlarmPresent == "0" else State.CRIT,
            summary="%s Alarms present - check online status!"
            % obj.upsAlarmPresent
            if obj.upsAlarmPresent != "0"
            else "No Alarms",
        ),
    },
    # --- Battery State ---
    {
        "name": "Battery State",
        "query": SNMPTree(base=nextUpsMIB + ".3", oids=["1"]),
        "keys": ["state"],
        "result": lambda obj, cfg: Result(
            state=State.UNKNOWN
            if obj.state == "0"
            else State.WARN
            if obj.state in ("3", "5")
            else State.OK
            if obj.state == "2"
            else State.CRIT,
            summary=BATTERY_STATE_MAP.get(obj.state, "unknown(%s)" % obj.state),
        ),
    },
    # --- Battery Temperature ---
    {
        "name": "Battery Temperature",
        "query": SNMPTree(base=nextUpsMIB + ".3", oids=["13"]),
        "keys": ["value"],
        "scale": 0.1,
        "metric_name": "oposs_next_temperature",
        "render_func": lambda v: "%.0f \u00b0C" % v,
        "default_params": {"levels_upper": ("fixed", (60.0, 70.0))},
        "boundaries": (0.0, 100.0),
        "ruleset_name": "oposs_next_ups_battery_temperature",
    },
    # --- Input Voltage (per-phase) ---
    *(
        {
            "name": "Phase %s Input Voltage" % name,
            "query": SNMPTree(base=nextUpsMIB + ".4.5.1", oids=["3.%s" % oid]),
            "keys": ["value"],
            "scale": 0.1,
            "metric_name": "oposs_next_voltage",
            "render_func": lambda v: "%.0f V" % v,
            "default_params": {"levels_lower": ("fixed", (210.0, 180.0))},
            "boundaries": (0.0, 250.0),
            "ruleset_name": "oposs_next_ups_input_voltage",
        }
        for name, oid in [("RS", "0"), ("ST", "1"), ("TR", "2")]
    ),
    # --- Input Frequency (per-phase, skip_zero) ---
    *(
        {
            "name": "Phase %s Input Frequency" % name,
            "query": SNMPTree(base=nextUpsMIB + ".4.5.1", oids=["2.%s" % oid]),
            "keys": ["value"],
            "scale": 0.1,
            "skip_zero": True,
            "metric_name": "oposs_next_frequency",
            "render_func": lambda v: "%.2f Hz" % v,
            "default_params": {
                "levels_lower": ("fixed", (49.0, 48.0)),
                "levels_upper": ("fixed", (51.0, 52.0)),
            },
            "boundaries": (0.0, 100.0),
            "ruleset_name": "oposs_next_ups_input_frequency",
        }
        for name, oid in [("RS", "0"), ("ST", "1"), ("TR", "2")]
    ),
    # --- Input Current (per-phase, info only) ---
    *(
        {
            "name": "Phase %s Input Current" % name,
            "query": SNMPTree(base=nextUpsMIB + ".4.5.1", oids=["4.%s" % oid]),
            "keys": ["value"],
            "scale": 0.1,
            "metric_name": "oposs_next_current",
            "render_func": lambda v: "%.0f A" % v,
            "default_params": {},
            "boundaries": (0.0, 1000.0),
        }
        for name, oid in [("RS", "0"), ("ST", "1"), ("TR", "2")]
    ),
    # --- Output Voltage (per-phase) ---
    *(
        {
            "name": "Phase %s Output Voltage" % name,
            "query": SNMPTree(base=nextUpsMIB + ".5.7.1", oids=["2.%s" % oid]),
            "keys": ["value"],
            "scale": 0.1,
            "metric_name": "oposs_next_voltage",
            "render_func": lambda v: "%.0f V" % v,
            "default_params": {"levels_lower": ("fixed", (210.0, 180.0))},
            "boundaries": (0.0, 250.0),
            "ruleset_name": "oposs_next_ups_output_voltage",
        }
        for name, oid in [("RS", "0"), ("ST", "1"), ("TR", "2")]
    ),
    # --- Output Frequency (per-phase, skip_zero) ---
    *(
        {
            "name": "Phase %s Output Frequency" % name,
            "query": SNMPTree(base=nextUpsMIB + ".5.7.1", oids=["9.%s" % oid]),
            "keys": ["value"],
            "scale": 0.1,
            "skip_zero": True,
            "metric_name": "oposs_next_frequency",
            "render_func": lambda v: "%.2f Hz" % v,
            "default_params": {
                "levels_lower": ("fixed", (49.0, 48.0)),
                "levels_upper": ("fixed", (51.0, 52.0)),
            },
            "boundaries": (0.0, 100.0),
            "ruleset_name": "oposs_next_ups_output_frequency",
        }
        for name, oid in [("RS", "0"), ("ST", "1"), ("TR", "2")]
    ),
    # --- Output Current (per-phase, info only) ---
    *(
        {
            "name": "Phase %s Output Current" % name,
            "query": SNMPTree(base=nextUpsMIB + ".5.7.1", oids=["3.%s" % oid]),
            "keys": ["value"],
            "scale": 0.1,
            "metric_name": "oposs_next_current",
            "render_func": lambda v: "%.0f A" % v,
            "default_params": {},
            "boundaries": (0.0, 1000.0),
        }
        for name, oid in [("RS", "0"), ("ST", "1"), ("TR", "2")]
    ),
    # --- Output Apparent Power (per-phase, info only) ---
    *(
        {
            "name": "Phase %s Output Apparent Power" % name,
            "query": SNMPTree(base=nextUpsMIB + ".5.7.1", oids=["4.%s" % oid]),
            "keys": ["value"],
            "scale": 100.0,
            "metric_name": "oposs_next_apparent_power",
            "render_func": lambda v: "%.1f kVA" % (v / 1000.0),
            "default_params": {},
            "boundaries": (0.0, 1200.0),
        }
        for name, oid in [("RS", "0"), ("ST", "1"), ("TR", "2")]
    ),
    # --- Output True Power (per-phase, info only; FIXED: kW not kVA) ---
    *(
        {
            "name": "Phase %s Output True Power" % name,
            "query": SNMPTree(base=nextUpsMIB + ".5.7.1", oids=["5.%s" % oid]),
            "keys": ["value"],
            "scale": 100.0,
            "metric_name": "oposs_next_true_power",
            "render_func": lambda v: "%.1f kW" % (v / 1000.0),
            "default_params": {},
            "boundaries": (0.0, 1200.0),
        }
        for name, oid in [("RS", "0"), ("ST", "1"), ("TR", "2")]
    ),
    # --- Output Load (per-phase) ---
    *(
        {
            "name": "Phase %s Output Load" % name,
            "query": SNMPTree(base=nextUpsMIB + ".5.7.1", oids=["7.%s" % oid]),
            "keys": ["value"],
            "scale": 1.0,
            "metric_name": "oposs_next_load_pct",
            "render_func": lambda v: "%.0f %%" % v,
            "default_params": {"levels_upper": ("fixed", (80.0, 90.0))},
            "boundaries": (0.0, 500.0),
            "ruleset_name": "oposs_next_ups_output_load",
        }
        for name, oid in [("RS", "0"), ("ST", "1"), ("TR", "2")]
    ),
    # --- Bypass Voltage (per-phase) ---
    *(
        {
            "name": "Phase %s Bypass Voltage" % name,
            "query": SNMPTree(base=nextUpsMIB + ".6.3.1", oids=["2.%s" % oid]),
            "keys": ["value"],
            "scale": 0.1,
            "metric_name": "oposs_next_voltage",
            "render_func": lambda v: "%.0f V" % v,
            "default_params": {"levels_lower": ("fixed", (210.0, 180.0))},
            "boundaries": (0.0, 250.0),
            "ruleset_name": "oposs_next_ups_bypass_voltage",
        }
        for name, oid in [("RS", "0"), ("ST", "1"), ("TR", "2")]
    ),
    # --- Bypass Current (per-phase, info only) ---
    *(
        {
            "name": "Phase %s Bypass Current" % name,
            "query": SNMPTree(base=nextUpsMIB + ".6.3.1", oids=["3.%s" % oid]),
            "keys": ["value"],
            "scale": 0.1,
            "metric_name": "oposs_next_current",
            "render_func": lambda v: "%.0f A" % v,
            "default_params": {},
            "boundaries": (0.0, 1000.0),
        }
        for name, oid in [("RS", "0"), ("ST", "1"), ("TR", "2")]
    ),
    # --- Bypass True Power (per-phase, info only; kW not kVA) ---
    *(
        {
            "name": "Phase %s Bypass True Power" % name,
            "query": SNMPTree(base=nextUpsMIB + ".6.3.1", oids=["5.%s" % oid]),
            "keys": ["value"],
            "scale": 100.0,
            "metric_name": "oposs_next_true_power",
            "render_func": lambda v: "%.1f kW" % (v / 1000.0),
            "default_params": {},
            "boundaries": (0.0, 1200.0),
        }
        for name, oid in [("RS", "0"), ("ST", "1"), ("TR", "2")]
    ),
    # --- Battery Voltage (info only) ---
    {
        "name": "Battery Voltage",
        "query": SNMPTree(base=upsMIB + ".2", oids=["5.0"]),
        "keys": ["value"],
        "scale": 0.1,
        "metric_name": "oposs_next_voltage",
        "render_func": lambda v: "%.1f V" % v,
        "default_params": {},
        "boundaries": (0.0, 2000.0),
    },
    # --- Battery Current (info only) ---
    {
        "name": "Battery Current",
        "query": SNMPTree(base=upsMIB + ".2", oids=["6.0"]),
        "keys": ["value"],
        "scale": 0.1,
        "metric_name": "oposs_next_current",
        "render_func": lambda v: "%.1f A" % v,
        "default_params": {},
        "boundaries": (-300.0, 300.0),
    },
    # --- Battery Charge Remaining ---
    {
        "name": "Battery Charge Remaining",
        "query": SNMPTree(base=upsMIB + ".2", oids=["4.0"]),
        "keys": ["value"],
        "scale": 1.0,
        "metric_name": "oposs_next_battery_pct",
        "render_func": lambda v: "%.0f %%" % v,
        "default_params": {"levels_lower": ("fixed", (15.0, 10.0))},
        "boundaries": (0.0, 100.0),
        "ruleset_name": "oposs_next_ups_battery_charge",
    },
    # --- Battery Time Remaining (minutes -> seconds) ---
    {
        "name": "Battery Time Remaining",
        "query": SNMPTree(base=upsMIB + ".2", oids=["3.0"]),
        "keys": ["value"],
        "scale": 60.0,
        "metric_name": "oposs_next_backup_time",
        "render_func": lambda v: "%.1fh" % (v / 3600.0),
        "default_params": {"levels_lower": ("fixed", (1200.0, 600.0))},
        "boundaries": (0.0, 3600.0),
        "ruleset_name": "oposs_next_ups_battery_time_remaining",
    },
    # --- Time On Battery (FIXED: OID "2.0" not "s.0") ---
    {
        "name": "Time On Battery",
        "query": SNMPTree(base=upsMIB + ".2", oids=["2.0"]),
        "keys": ["value"],
        "scale": 1.0,
        "metric_name": "oposs_next_backup_time",
        "render_func": lambda v: "%.1fh" % (v / 3600.0),
        "default_params": {"levels_upper": ("fixed", (60.0, 300.0))},
        "boundaries": (0.0, 3600.0),
        "ruleset_name": "oposs_next_ups_time_on_battery",
    },
]


# ---------------------------------------------------------------------------
# Dynamic plugin generation
# ---------------------------------------------------------------------------


def _make_plugins(cfg):
    """Generate SimpleSNMPSection + CheckPlugin module-level variables."""
    check_key = "oposs_next_ups_%s" % cfg["name"].lower().replace(" ", "_")
    obj_class = namedtuple(check_key, cfg["keys"])

    def parse_fn(string_table):
        for row in string_table:
            return obj_class(*row)
        return None

    def discovery_fn(section):
        if section:
            yield Service()

    if "result" in cfg:
        # State-mapping check — no params
        def check_fn(section):
            if not section:
                return
            yield cfg["result"](section, cfg)

        cp_kwargs = {}
    else:
        # check_levels check — with params
        def check_fn(params, section):
            if not section:
                return
            if cfg.get("skip_zero") and int(section.value) == 0:
                value = float("nan")
            else:
                value = cfg.get("scale", 1.0) * float(section.value)
            yield from check_levels(
                value=value,
                levels_upper=params.get("levels_upper"),
                levels_lower=params.get("levels_lower"),
                boundaries=cfg.get("boundaries"),
                metric_name=cfg["metric_name"],
                render_func=cfg["render_func"],
                label=cfg["name"],
            )

        cp_kwargs = {
            "check_default_parameters": cfg["default_params"],
        }
        if "ruleset_name" in cfg:
            cp_kwargs["check_ruleset_name"] = cfg["ruleset_name"]

    globals()["snmp_section_%s" % check_key] = SimpleSNMPSection(
        name=check_key,
        detect=DETECT_NEXT_UPS,
        parse_function=parse_fn,
        fetch=cfg["query"],
    )

    globals()["check_plugin_%s" % check_key] = CheckPlugin(
        name=check_key,
        sections=[check_key],
        service_name=cfg["name"],
        discovery_function=discovery_fn,
        check_function=check_fn,
        **cp_kwargs,
    )


for _cfg in targets:
    _make_plugins(_cfg)
