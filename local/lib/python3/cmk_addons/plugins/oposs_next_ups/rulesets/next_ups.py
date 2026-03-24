#!/usr/bin/env python3

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    LevelDirection,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostCondition,
    Topic,
)


def _upper_levels(title, unit, default):
    return Dictionary(
        elements={
            "levels_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("%s" % title),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol=unit),
                    prefill_fixed_levels=DefaultValue(default),
                ),
                required=True,
            ),
        },
    )


def _lower_levels(title, unit, default):
    return Dictionary(
        elements={
            "levels_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("%s" % title),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Float(unit_symbol=unit),
                    prefill_fixed_levels=DefaultValue(default),
                ),
                required=True,
            ),
        },
    )


def _upper_lower_levels(title_upper, title_lower, unit, default_upper, default_lower):
    return Dictionary(
        elements={
            "levels_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("%s" % title_upper),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol=unit),
                    prefill_fixed_levels=DefaultValue(default_upper),
                ),
                required=True,
            ),
            "levels_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("%s" % title_lower),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Float(unit_symbol=unit),
                    prefill_fixed_levels=DefaultValue(default_lower),
                ),
                required=True,
            ),
        },
    )


# --- Battery Temperature ---

rule_spec_oposs_next_ups_battery_temperature = CheckParameters(
    name="oposs_next_ups_battery_temperature",
    title=Title("NextUPS Battery Temperature"),
    topic=Topic.ENVIRONMENTAL,
    parameter_form=lambda: _upper_levels("Upper levels", "\u00b0C", (60.0, 70.0)),
    condition=HostCondition(),
)

# --- Voltage rulesets ---

rule_spec_oposs_next_ups_input_voltage = CheckParameters(
    name="oposs_next_ups_input_voltage",
    title=Title("NextUPS Input Voltage"),
    topic=Topic.POWER,
    parameter_form=lambda: _lower_levels("Lower levels", "V", (210.0, 180.0)),
    condition=HostCondition(),
)

rule_spec_oposs_next_ups_output_voltage = CheckParameters(
    name="oposs_next_ups_output_voltage",
    title=Title("NextUPS Output Voltage"),
    topic=Topic.POWER,
    parameter_form=lambda: _lower_levels("Lower levels", "V", (210.0, 180.0)),
    condition=HostCondition(),
)

rule_spec_oposs_next_ups_bypass_voltage = CheckParameters(
    name="oposs_next_ups_bypass_voltage",
    title=Title("NextUPS Bypass Voltage"),
    topic=Topic.POWER,
    parameter_form=lambda: _lower_levels("Lower levels", "V", (210.0, 180.0)),
    condition=HostCondition(),
)

# --- Frequency rulesets ---

rule_spec_oposs_next_ups_input_frequency = CheckParameters(
    name="oposs_next_ups_input_frequency",
    title=Title("NextUPS Input Frequency"),
    topic=Topic.POWER,
    parameter_form=lambda: _upper_lower_levels(
        "Upper levels", "Lower levels", "Hz", (51.0, 52.0), (49.0, 48.0),
    ),
    condition=HostCondition(),
)

rule_spec_oposs_next_ups_output_frequency = CheckParameters(
    name="oposs_next_ups_output_frequency",
    title=Title("NextUPS Output Frequency"),
    topic=Topic.POWER,
    parameter_form=lambda: _upper_lower_levels(
        "Upper levels", "Lower levels", "Hz", (51.0, 52.0), (49.0, 48.0),
    ),
    condition=HostCondition(),
)

# --- Load ---

rule_spec_oposs_next_ups_output_load = CheckParameters(
    name="oposs_next_ups_output_load",
    title=Title("NextUPS Output Load"),
    topic=Topic.POWER,
    parameter_form=lambda: _upper_levels("Upper levels", "%", (80.0, 90.0)),
    condition=HostCondition(),
)

# --- Battery ---

rule_spec_oposs_next_ups_battery_charge = CheckParameters(
    name="oposs_next_ups_battery_charge",
    title=Title("NextUPS Battery Charge Remaining"),
    topic=Topic.POWER,
    parameter_form=lambda: _lower_levels("Lower levels", "%", (15.0, 10.0)),
    condition=HostCondition(),
)

rule_spec_oposs_next_ups_battery_time_remaining = CheckParameters(
    name="oposs_next_ups_battery_time_remaining",
    title=Title("NextUPS Battery Time Remaining"),
    topic=Topic.POWER,
    parameter_form=lambda: _lower_levels("Lower levels", "s", (1200.0, 600.0)),
    condition=HostCondition(),
)

rule_spec_oposs_next_ups_time_on_battery = CheckParameters(
    name="oposs_next_ups_time_on_battery",
    title=Title("NextUPS Time On Battery"),
    topic=Topic.POWER,
    parameter_form=lambda: _upper_levels("Upper levels", "s", (60.0, 300.0)),
    condition=HostCondition(),
)
