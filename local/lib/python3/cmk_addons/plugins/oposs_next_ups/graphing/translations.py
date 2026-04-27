#!/usr/bin/env python3
# Copyright (C) 2025 OETIKER+PARTNER AG - License: GNU General Public License v2

"""Metric translations for the Next UPS plugin rename.

The legacy plugin used check command names ``next_ups_<service>`` with
generic metric names (``temperature``, ``voltage``, ``current``,
``frequency``, ``power``, ``percentage``, ``duration``).  The v2 plugin
uses ``oposs_next_ups_<service>`` check commands and prefixed
``oposs_next_*`` metrics.

IMPORTANT: ``check_commands`` MUST reference the *new* check command (the
one the live service has today). Checkmk's translation lookup
(``cmk/gui/graphing/_translated_metrics.py``,
``lookup_metric_translations_for_check_command``) is an exact dict-key
match against that command — entries keyed on the legacy ``next_ups_*``
command would never fire after the legacy plugin is uninstalled, leaving
the legacy generic-named RRD files orphaned in the per-service
directories. Service names are unchanged across both plugins, so the
legacy ``voltage.rrd`` etc. coexist with the new ``oposs_next_voltage.rrd``
in the same directory and the rename rules below stitch them into
continuous graphs.
"""

from cmk.graphing.v1 import translations

# --- Temperature ---

translation_oposs_next_ups_battery_temperature = translations.Translation(
    name="oposs_next_ups_battery_temperature",
    check_commands=[translations.PassiveCheck("oposs_next_ups_battery_temperature")],
    translations={"temperature": translations.RenameTo("oposs_next_temperature")},
)

# --- Input Voltage (per-phase RS/ST/TR) ---

translation_oposs_next_ups_phase_rs_input_voltage = translations.Translation(
    name="oposs_next_ups_phase_rs_input_voltage",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_rs_input_voltage")],
    translations={"voltage": translations.RenameTo("oposs_next_voltage")},
)

translation_oposs_next_ups_phase_st_input_voltage = translations.Translation(
    name="oposs_next_ups_phase_st_input_voltage",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_st_input_voltage")],
    translations={"voltage": translations.RenameTo("oposs_next_voltage")},
)

translation_oposs_next_ups_phase_tr_input_voltage = translations.Translation(
    name="oposs_next_ups_phase_tr_input_voltage",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_tr_input_voltage")],
    translations={"voltage": translations.RenameTo("oposs_next_voltage")},
)

# --- Output Voltage (per-phase) ---

translation_oposs_next_ups_phase_rs_output_voltage = translations.Translation(
    name="oposs_next_ups_phase_rs_output_voltage",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_rs_output_voltage")],
    translations={"voltage": translations.RenameTo("oposs_next_voltage")},
)

translation_oposs_next_ups_phase_st_output_voltage = translations.Translation(
    name="oposs_next_ups_phase_st_output_voltage",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_st_output_voltage")],
    translations={"voltage": translations.RenameTo("oposs_next_voltage")},
)

translation_oposs_next_ups_phase_tr_output_voltage = translations.Translation(
    name="oposs_next_ups_phase_tr_output_voltage",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_tr_output_voltage")],
    translations={"voltage": translations.RenameTo("oposs_next_voltage")},
)

# --- Bypass Voltage (per-phase) ---

translation_oposs_next_ups_phase_rs_bypass_voltage = translations.Translation(
    name="oposs_next_ups_phase_rs_bypass_voltage",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_rs_bypass_voltage")],
    translations={"voltage": translations.RenameTo("oposs_next_voltage")},
)

translation_oposs_next_ups_phase_st_bypass_voltage = translations.Translation(
    name="oposs_next_ups_phase_st_bypass_voltage",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_st_bypass_voltage")],
    translations={"voltage": translations.RenameTo("oposs_next_voltage")},
)

translation_oposs_next_ups_phase_tr_bypass_voltage = translations.Translation(
    name="oposs_next_ups_phase_tr_bypass_voltage",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_tr_bypass_voltage")],
    translations={"voltage": translations.RenameTo("oposs_next_voltage")},
)

# --- Battery Voltage ---

translation_oposs_next_ups_battery_voltage = translations.Translation(
    name="oposs_next_ups_battery_voltage",
    check_commands=[translations.PassiveCheck("oposs_next_ups_battery_voltage")],
    translations={"voltage": translations.RenameTo("oposs_next_voltage")},
)

# --- Input Frequency (per-phase) ---

translation_oposs_next_ups_phase_rs_input_frequency = translations.Translation(
    name="oposs_next_ups_phase_rs_input_frequency",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_rs_input_frequency")],
    translations={"frequency": translations.RenameTo("oposs_next_frequency")},
)

translation_oposs_next_ups_phase_st_input_frequency = translations.Translation(
    name="oposs_next_ups_phase_st_input_frequency",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_st_input_frequency")],
    translations={"frequency": translations.RenameTo("oposs_next_frequency")},
)

translation_oposs_next_ups_phase_tr_input_frequency = translations.Translation(
    name="oposs_next_ups_phase_tr_input_frequency",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_tr_input_frequency")],
    translations={"frequency": translations.RenameTo("oposs_next_frequency")},
)

# --- Output Frequency (per-phase) ---

translation_oposs_next_ups_phase_rs_output_frequency = translations.Translation(
    name="oposs_next_ups_phase_rs_output_frequency",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_rs_output_frequency")],
    translations={"frequency": translations.RenameTo("oposs_next_frequency")},
)

translation_oposs_next_ups_phase_st_output_frequency = translations.Translation(
    name="oposs_next_ups_phase_st_output_frequency",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_st_output_frequency")],
    translations={"frequency": translations.RenameTo("oposs_next_frequency")},
)

translation_oposs_next_ups_phase_tr_output_frequency = translations.Translation(
    name="oposs_next_ups_phase_tr_output_frequency",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_tr_output_frequency")],
    translations={"frequency": translations.RenameTo("oposs_next_frequency")},
)

# --- Input Current (per-phase) ---

translation_oposs_next_ups_phase_rs_input_current = translations.Translation(
    name="oposs_next_ups_phase_rs_input_current",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_rs_input_current")],
    translations={"current": translations.RenameTo("oposs_next_current")},
)

translation_oposs_next_ups_phase_st_input_current = translations.Translation(
    name="oposs_next_ups_phase_st_input_current",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_st_input_current")],
    translations={"current": translations.RenameTo("oposs_next_current")},
)

translation_oposs_next_ups_phase_tr_input_current = translations.Translation(
    name="oposs_next_ups_phase_tr_input_current",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_tr_input_current")],
    translations={"current": translations.RenameTo("oposs_next_current")},
)

# --- Output Current (per-phase) ---

translation_oposs_next_ups_phase_rs_output_current = translations.Translation(
    name="oposs_next_ups_phase_rs_output_current",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_rs_output_current")],
    translations={"current": translations.RenameTo("oposs_next_current")},
)

translation_oposs_next_ups_phase_st_output_current = translations.Translation(
    name="oposs_next_ups_phase_st_output_current",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_st_output_current")],
    translations={"current": translations.RenameTo("oposs_next_current")},
)

translation_oposs_next_ups_phase_tr_output_current = translations.Translation(
    name="oposs_next_ups_phase_tr_output_current",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_tr_output_current")],
    translations={"current": translations.RenameTo("oposs_next_current")},
)

# --- Bypass Current (per-phase) ---

translation_oposs_next_ups_phase_rs_bypass_current = translations.Translation(
    name="oposs_next_ups_phase_rs_bypass_current",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_rs_bypass_current")],
    translations={"current": translations.RenameTo("oposs_next_current")},
)

translation_oposs_next_ups_phase_st_bypass_current = translations.Translation(
    name="oposs_next_ups_phase_st_bypass_current",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_st_bypass_current")],
    translations={"current": translations.RenameTo("oposs_next_current")},
)

translation_oposs_next_ups_phase_tr_bypass_current = translations.Translation(
    name="oposs_next_ups_phase_tr_bypass_current",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_tr_bypass_current")],
    translations={"current": translations.RenameTo("oposs_next_current")},
)

# --- Battery Current ---

translation_oposs_next_ups_battery_current = translations.Translation(
    name="oposs_next_ups_battery_current",
    check_commands=[translations.PassiveCheck("oposs_next_ups_battery_current")],
    translations={"current": translations.RenameTo("oposs_next_current")},
)

# --- Output Apparent Power (per-phase) ---

translation_oposs_next_ups_phase_rs_output_apparent_power = translations.Translation(
    name="oposs_next_ups_phase_rs_output_apparent_power",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_rs_output_apparent_power")],
    translations={"power": translations.RenameTo("oposs_next_apparent_power")},
)

translation_oposs_next_ups_phase_st_output_apparent_power = translations.Translation(
    name="oposs_next_ups_phase_st_output_apparent_power",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_st_output_apparent_power")],
    translations={"power": translations.RenameTo("oposs_next_apparent_power")},
)

translation_oposs_next_ups_phase_tr_output_apparent_power = translations.Translation(
    name="oposs_next_ups_phase_tr_output_apparent_power",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_tr_output_apparent_power")],
    translations={"power": translations.RenameTo("oposs_next_apparent_power")},
)

# --- Output True Power (per-phase) ---

translation_oposs_next_ups_phase_rs_output_true_power = translations.Translation(
    name="oposs_next_ups_phase_rs_output_true_power",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_rs_output_true_power")],
    translations={"power": translations.RenameTo("oposs_next_true_power")},
)

translation_oposs_next_ups_phase_st_output_true_power = translations.Translation(
    name="oposs_next_ups_phase_st_output_true_power",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_st_output_true_power")],
    translations={"power": translations.RenameTo("oposs_next_true_power")},
)

translation_oposs_next_ups_phase_tr_output_true_power = translations.Translation(
    name="oposs_next_ups_phase_tr_output_true_power",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_tr_output_true_power")],
    translations={"power": translations.RenameTo("oposs_next_true_power")},
)

# --- Bypass True Power (per-phase) ---

translation_oposs_next_ups_phase_rs_bypass_true_power = translations.Translation(
    name="oposs_next_ups_phase_rs_bypass_true_power",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_rs_bypass_true_power")],
    translations={"power": translations.RenameTo("oposs_next_true_power")},
)

translation_oposs_next_ups_phase_st_bypass_true_power = translations.Translation(
    name="oposs_next_ups_phase_st_bypass_true_power",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_st_bypass_true_power")],
    translations={"power": translations.RenameTo("oposs_next_true_power")},
)

translation_oposs_next_ups_phase_tr_bypass_true_power = translations.Translation(
    name="oposs_next_ups_phase_tr_bypass_true_power",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_tr_bypass_true_power")],
    translations={"power": translations.RenameTo("oposs_next_true_power")},
)

# --- Output Load (per-phase) ---

translation_oposs_next_ups_phase_rs_output_load = translations.Translation(
    name="oposs_next_ups_phase_rs_output_load",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_rs_output_load")],
    translations={"percentage": translations.RenameTo("oposs_next_load_pct")},
)

translation_oposs_next_ups_phase_st_output_load = translations.Translation(
    name="oposs_next_ups_phase_st_output_load",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_st_output_load")],
    translations={"percentage": translations.RenameTo("oposs_next_load_pct")},
)

translation_oposs_next_ups_phase_tr_output_load = translations.Translation(
    name="oposs_next_ups_phase_tr_output_load",
    check_commands=[translations.PassiveCheck("oposs_next_ups_phase_tr_output_load")],
    translations={"percentage": translations.RenameTo("oposs_next_load_pct")},
)

# --- Battery Charge ---

translation_oposs_next_ups_battery_charge_remaining = translations.Translation(
    name="oposs_next_ups_battery_charge_remaining",
    check_commands=[translations.PassiveCheck("oposs_next_ups_battery_charge_remaining")],
    translations={"percentage": translations.RenameTo("oposs_next_battery_pct")},
)

# --- Battery Time Remaining ---

translation_oposs_next_ups_battery_time_remaining = translations.Translation(
    name="oposs_next_ups_battery_time_remaining",
    check_commands=[translations.PassiveCheck("oposs_next_ups_battery_time_remaining")],
    translations={"duration": translations.RenameTo("oposs_next_time_remaining")},
)

# --- Time On Battery ---

translation_oposs_next_ups_time_on_battery = translations.Translation(
    name="oposs_next_ups_time_on_battery",
    check_commands=[translations.PassiveCheck("oposs_next_ups_time_on_battery")],
    translations={"duration": translations.RenameTo("oposs_next_time_on_battery")},
)
