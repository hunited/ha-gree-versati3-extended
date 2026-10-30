"""Constants for the Gree Versati Extended integration."""

from __future__ import annotations

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "gree_versati_extended"

CONF_DEVICE_ID: Final = "device_id"
CONF_KEY: Final = "key"
CONF_TIMEOUT: Final = "timeout"
CONF_SCAN_INTERVAL: Final = "scan_interval"

DEFAULT_PORT: Final = 7000
DEFAULT_TIMEOUT: Final = 5
DEFAULT_SCAN_INTERVAL: Final = 300
DEFAULT_RETRIES: Final = 2

MIN_HE_WAT_OUT_TEMP_SET: Final = 20
MAX_HE_WAT_OUT_TEMP_SET: Final = 60
HE_WAT_OUT_TEMP_SET_STEP: Final = 1

MIN_CO_WAT_OUT_TEMP_SET: Final = 5
MAX_CO_WAT_OUT_TEMP_SET: Final = 25
CO_WAT_OUT_TEMP_SET_STEP: Final = 1

MIN_WAT_BOX_TEMP_SET: Final = 20
MAX_WAT_BOX_TEMP_SET: Final = 60
WAT_BOX_TEMP_SET_STEP: Final = 1

MIN_HE_HOM_TEMP_SET: Final = 16
MAX_HE_HOM_TEMP_SET: Final = 30
HE_HOM_TEMP_SET_STEP: Final = 1

MIN_CO_HOM_TEMP_SET: Final = 18
MAX_CO_HOM_TEMP_SET: Final = 30
CO_HOM_TEMP_SET_STEP: Final = 1

PARAM_HE_WAT_OUT_TEM_SET: Final = "HeWatOutTemSet"
PARAM_CO_WAT_OUT_TEM_SET: Final = "CoWatOutTemSet"
PARAM_WAT_BOX_TEM_SET: Final = "WatBoxTemSet"
PARAM_HE_HOM_TEMP_SET: Final = "HeHomTemSet"
PARAM_CO_HOM_TEMP_SET: Final = "CoHomTemSet"
PARAM_TEM_UN: Final = "TemUn"
PARAM_ALL_ERR: Final = "AllErr"
PARAM_MOD: Final = "Mod"
PARAM_POW: Final = "Pow"
PARAM_QUIET: Final = "Quiet"

TEMPERATURE_SENSORS: Final[tuple[tuple[str, str, str], ...]] = (
    ("wat_box_tem", "WatBoxTemHi", "WatBoxTemLo"),
    ("all_out_wat_tem", "AllOutWatTemHi", "AllOutWatTemLo"),
    ("all_in_wat_tem", "AllInWatTemHi", "AllInWatTemLo"),
    ("hep_out_wat_tem", "HepOutWatTemHi", "HepOutWatTemLo"),
    ("rmo_hom_tem", "RmoHomTemHi", "RmoHomTemLo"),
)

EXTRA_SENSOR_PARAMETERS: Final[tuple[tuple[str, str], ...]] = (
    ("SetTem", "set_tem"),
    ("WdSpd", "fan_speed"),
    ("Air", "fresh_air"),
    ("Blo", "x_fan"),
    ("Health", "health_function"),
    ("SwhSlp", "sleep_mode"),
    ("Lig", "display_light"),
    ("SwingLfRig", "horizontal_swing"),
    ("SwUpDn", "vertical_swing"),
    ("Tur", "turbo_mode"),
    ("StHt", "frost_protection"),
    ("HeatCoolType", "heat_cool_type"),
    ("TemRec", "temperature_recovery"),
    ("SvSt", "energy_saving"),
    ("time", "device_time"),
    ("AllInWatTem", "raw_water_return_temperature"),
    ("AllOutWatTem", "raw_water_supply_temperature"),
    ("Emegcy", "emergency_status"),
    ("ColHtWter", "cooling_hot_water_option"),
    ("HetHtWter", "heating_hot_water_option"),
    ("TemRecB", "temperature_recovery_secondary"),
    ("FastHtWter", "fast_hot_water"),
    ("LefHom", "leave_home_mode"),
    ("SwDisFct", "display_function_switch"),
    ("VersatiSeries", "versati_series"),
    ("RomHomTemExt", "external_room_temperature"),
    ("WatBoxExt", "external_water_tank"),
    ("FocModSwh", "forced_mode_switch"),
    ("HanFroSwh", "manual_frost_switch"),
    ("WatSyExhSwh", "water_system_exhaust"),
    ("BordTest", "board_test"),
    ("ColColetSwh", "collector_cooling_switch"),
    ("EndTemCotSwh", "end_temperature_control_switch"),
    ("ModelType", "model_type"),
    ("WatBoxElcHeRunSta", "tank_electric_heater_status"),
    ("SyAnFroRunSta", "system_antifreeze_status"),
    ("ElcHe1RunSta", "electric_heater_1_status"),
    ("ElcHe2RunSta", "electric_heater_2_status"),
    ("AnFrzzRunSta", "antifreeze_status"),
    ("SorErr", "source_error"),
    ("CommErr", "communication_error"),
)

DIAGNOSTIC_SENSOR_PARAMETERS: Final[frozenset[str]] = frozenset(
    {
        PARAM_ALL_ERR,
        "Emegcy",
        "FocModSwh",
        "HanFroSwh",
        "WatSyExhSwh",
        "BordTest",
        "ColColetSwh",
        "EndTemCotSwh",
        "WatBoxElcHeRunSta",
        "SyAnFroRunSta",
        "ElcHe1RunSta",
        "ElcHe2RunSta",
        "AnFrzzRunSta",
        "SorErr",
        "CommErr",
        "HeatCoolType",
        "ModelType",
        "TemRecB",
        "LefHom",
    }
)

BOOLEAN_SENSOR_PARAMETERS: Final[frozenset[str]] = frozenset(
    {
        "Air",
        "Blo",
        "Health",
        "SwhSlp",
        "Lig",
        "SwingLfRig",
        "SwUpDn",
        "Tur",
        "StHt",
        "TemRec",
        "SvSt",
        "Emegcy",
        "ColHtWter",
        "HetHtWter",
        "TemRecB",
        "FastHtWter",
        "LefHom",
        "SwDisFct",
        "RomHomTemExt",
        "WatBoxExt",
        "FocModSwh",
        "HanFroSwh",
        "WatSyExhSwh",
        "BordTest",
        "ColColetSwh",
        "EndTemCotSwh",
        "WatBoxElcHeRunSta",
        "SyAnFroRunSta",
        "ElcHe1RunSta",
        "ElcHe2RunSta",
        "AnFrzzRunSta",
    }
)

POLL_KEYS: Final[tuple[str, ...]] = (
    PARAM_HE_WAT_OUT_TEM_SET,
    PARAM_CO_WAT_OUT_TEM_SET,
    PARAM_WAT_BOX_TEM_SET,
    PARAM_HE_HOM_TEMP_SET,
    PARAM_CO_HOM_TEMP_SET,
    PARAM_TEM_UN,
    PARAM_ALL_ERR,
    PARAM_MOD,
    PARAM_POW,
    PARAM_QUIET,
    *(key for _, hi_key, lo_key in TEMPERATURE_SENSORS for key in (hi_key, lo_key)),
    *(param_key for param_key, _ in EXTRA_SENSOR_PARAMETERS),
)

SERVICE_SET_PARAM: Final = "set_param"
SERVICE_GET_PARAMS: Final = "get_params"

ATTR_KEY: Final = "key"
ATTR_KEYS: Final = "keys"
ATTR_VALUE: Final = "value"

DEFAULT_MAX_DATAGRAM_BYTES: Final = 8192

DATA_ENTRIES: Final = "entries"
DATA_CLIENT: Final = "client"
DATA_COORDINATOR: Final = "coordinator"

MODE_OPTIONS: Final[dict[str, int]] = {
    "heat": 1,
    "cool": 5,
    "hot_water": 2,
    "cool_hot_water": 3,
    "heat_hot_water": 4,
}

PLATFORMS: Final[list[Platform]] = [
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
]
