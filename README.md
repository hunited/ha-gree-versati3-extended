# Gree Versati 3 Local Extended
Based on https://github.com/sarunasr/ha-gree-versati3 and extended. Use it like they do:

Custom Home Assistant integration for local LAN control of a Gree Versati 3 heat pump over the device UDP JSON protocol.

This integration is inspired by protocol behavior observed in [`tomikaa87/gree-remote`](https://github.com/tomikaa87/gree-remote), but implemented from scratch in this repository without vendoring or subprocess calls.

## Features

- Local UDP communication (no cloud dependency)
- AES `pack` payload support for both ECB and GCM devices (auto-detected)
- Config Flow + Config Entry setup
- DataUpdateCoordinator polling (default 30s, configurable)
- Five temperature setpoint number entities:
  - Heating water outlet: 20..60 °C
  - Cooling water outlet: 5..25 °C
  - Hot water tank: 20..60 °C
  - Room heating: 16..30 °C
  - Room cooling: 18..30 °C
- Switch entities for power and quiet mode
- Operation mode selector (`Heat`, `Cool`, `Hot water`, `Cool + hot water`, `Heat + hot water`)
- Sensors (unavailable when the device omits the corresponding values):
  - Setpoints: heating/cooling water outlet, hot water tank, room heating/cooling
  - Device values: temperature unit, error code, operation mode, power
  - Temperatures: hot water tank, heating circuit supply and return, heat exchanger outlet, remote room
  - Additional raw protocol sensors for the extra parameters listed below
- Services:
  - `gree_versati_extended.set_param`
  - `gree_versati_extended.get_params`
- Custom integration icon (shown directly by Home Assistant 2026.3 and newer)

The mode selector requires the unit to be off before changing modes. The calculated
temperature sensors require both device registers for that measurement.

## Additional device parameters

The integration polls and exposes these additional values as read-only sensors:

- General Gree controls/status: `SetTem`, `WdSpd`, `Air`, `Blo`, `Health`,
  `SwhSlp`, `Lig`, `SwingLfRig`, `SwUpDn`, `Tur`, `StHt`, `HeatCoolType`,
  `TemRec`, `SvSt`
- Versati options and operating status: `Emegcy`, `ColHtWter`, `HetHtWter`,
  `TemRecB`, `FastHtWter`, `LefHom`, `SwDisFct`, `VersatiSeries`,
  `RomHomTemExt`, `WatBoxExt`, `FocModSwh`, `HanFroSwh`, `WatSyExhSwh`,
  `BordTest`, `ColColetSwh`, `EndTemCotSwh`, `WatBoxElcHeRunSta`,
  `SyAnFroRunSta`, `ElcHe1RunSta`, `ElcHe2RunSta`, `AnFrzzRunSta`,
  `SorErr`, `CommErr`
- Other returned values: `time`, `ModelType`, `AllInWatTem`, `AllOutWatTem`

The names and meanings of several values come from the general Gree protocol and
may differ by heat-pump model or firmware. Clearly recognizable values such as
`WdSpd` (fan speed), `SwingLfRig`/`SwUpDn` (horizontal/vertical airflow direction),
`SwhSlp` (sleep mode), `Quiet` (quiet mode), `Tur` (turbo), and `SvSt`
(energy-saving mode) are shown with descriptive names. Values whose meaning or
enumeration is not confirmed for this Versati model remain raw protocol readings;
the integration does not guess their meaning or offer them as controls.

### Optional diagnostic sensors

The following diagnostic, service, or not-yet-confirmed sensor entities are
created **disabled by default** to keep the entity list focused:

`AllErr`, `Emegcy`, `FocModSwh`, `HanFroSwh`, `WatSyExhSwh`, `BordTest`,
`ColColetSwh`, `EndTemCotSwh`, `WatBoxElcHeRunSta`, `SyAnFroRunSta`,
`ElcHe1RunSta`, `ElcHe2RunSta`, `AnFrzzRunSta`, `SorErr`, `CommErr`,
`HeatCoolType`, `ModelType`, `TemRecB`, and `LefHom`.

They are still polled and can be enabled individually in Home Assistant under
**Settings → Devices & services → Entities** (enable disabled entities). The
disabled state only affects the sensor entity; it does not remove a parameter
from protocol polling. Names for several service and diagnostic flags are
tentative, model-dependent interpretations, not confirmed Versati documentation.
In particular, the proposed meanings of `FocModSwh`, `HanFroSwh`, `WatSyExhSwh`,
`BordTest`, `ColColetSwh`, `EndTemCotSwh`, `HeatCoolType`, `ModelType`,
`TemRecB`, and `LefHom` should be treated as unverified. These parameters are
exposed as sensors, not as dedicated controls.

Based on the owner's observations, `ColHtWter` and `HetHtWter` are cooling and
heating hot-water enable flags; `VersatiSeries = 7` identifies Versati III;
`FastHtWter` is rapid hot-water mode; `SwDisFct` is tank disinfection
(anti-legionella heating using the electric element); `RomHomTemExt` indicates
an external room sensor; and `WatBoxExt` indicates the auxiliary tank heater.
These interpretations are useful device-specific observations, not universal
protocol guarantees.

References used for protocol investigation:

- [gree-remote issue #59](https://github.com/tomikaa87/gree-remote/issues/59)
- [gree-remote issue #56](https://github.com/tomikaa87/gree-remote/issues/56)
- [gree-remote issue #43](https://github.com/tomikaa87/gree-remote/issues/43)
- [Gree Versati parameter notes](https://gist.github.com/kostirez1/7140739d2d49d60f11eee7552b6e10b9)
- [Additional Gree Versati notes](https://gist.github.com/kostirez1/b9588e4f355a8bb974a282af439fafb1)

`SetTem` is a generic Gree set-temperature parameter and is not the Versati room
setpoint. The Versati exposes separate heating and cooling targets: `HeHomTemSet`
is the desired room temperature in heating mode, while `CoHomTemSet` is the
desired room temperature in cooling mode. They are configured independently.
The water outlet and hot-water tank targets are also separate settings.

The direct `AllInWatTem` and `AllOutWatTem` values may be zero on this model,
including when they do not provide useful live readings. The integration instead
calculates return, supply, heat-exchanger, tank, and remote-room temperatures
from their `Hi`/`Lo` register pairs using `Hi - 100 + (Lo / 10)`. These are
measured temperatures, not target setpoints. Some readings may only be useful
while the circulation pump is running.

For the example registers provided during development, the formula gives 23.2 °C
return water, 23.6 °C supply water, 23.0 °C heat-exchanger outlet, 50.2 °C
hot-water tank, and 22.3 °C remote room temperature.

`Pow = 1` means the unit is on, `Quiet = 0` means quiet mode is off, and
`Mod = 4` maps to “Heat + hot water” in this integration. `AllErr = 0` is the
device-reported error value; consult the heat-pump manual for model-specific
interpretation.

## Services

`gree_versati_extended.set_param` writes one protocol parameter. `key` and `value`
are required; `device_id` is optional. If omitted, the command is sent to every
configured device.

`gree_versati_extended.get_params` reads a list of protocol parameters. `keys` is
required; `device_id` is optional. If omitted, the response contains results for
every configured device.

Example data for `set_param`:

```yaml
key: Pow
value: 1
```

Example data for `get_params`:

```yaml
keys:
  - Pow
  - Quiet
```

## Install via HACS (Custom Repository)

1. Open HACS in Home Assistant.
2. Go to `Integrations`.
3. Open the menu (`⋮`) and choose `Custom repositories`.
4. Add this repository URL and category `Integration`.
5. Install `Gree Versati 3 Extended` from HACS.
6. Restart Home Assistant.
7. Add integration: `Settings` -> `Devices & Services` -> `Add Integration` -> `Gree Versati 3 Local Extended`.

## Configuration Fields

- `host`: Heat pump IP or hostname
- `port`: UDP port (default `7000`)
- `device_id`: Device identifier used by protocol envelope
- `key`: 16-byte AES key string
- `timeout`: UDP timeout in seconds (default `5`)

Options flow:
- `scan_interval`: Polling interval in seconds (default `30`)

## Notes

- The AES key must be exactly 16 bytes (UTF-8 byte length).
- The integration does not log the key.
- If a parameter is not returned by the device, corresponding entities are marked unavailable.

## Getting `device_id` and `key`

If you do not know the `device_id` and `key`, you can obtain them with `gree-remote`:

1. Clone the tool:

```bash
git clone https://github.com/tomikaa87/gree-remote
cd gree-remote
```

2. Search/bind to retrieve device credentials:

```bash
python3 PythonCLI/gree.py search -b <gree-ip>
```

The output should include the discovered device ID and bound key.

Note: in many networks, `-b` should be the subnet broadcast address (for example `192.168.1.255`), but some setups may work using the device IP directly.

3. Verify credentials by reading a known parameter:

```bash
python3 PythonCLI/gree.py -c <gree-ip> -i <id> -k <key> get HeWatOutTemSet
```

If this returns a value, use the same `host`, `device_id`, and `key` in this Home Assistant integration.

### Troubleshooting key retrieval

- Ensure your laptop/host and the heat pump are on the same subnet.
- Avoid guest Wi-Fi networks (client/AP isolation can block UDP device discovery).
- Try broadcast address for your subnet (for `/24`, usually `x.x.x.255`).
- If you have multiple interfaces (Ethernet + Wi-Fi), bind `gree.py` to the correct one:

```bash
python3 PythonCLI/gree.py --socket-interface <iface> search -b <broadcast_ip>
```

- If `search` fails but direct `get` works with known credentials, discovery traffic may be blocked while unicast traffic still works.

## Legal / Licensing Note

This repository is original MIT-licensed code.

Protocol behavior was implemented based on reverse engineering and public interoperability knowledge. No direct source copy from `gree-remote` is included.

You are responsible for complying with local laws, device warranties, and network/security policies when using reverse-engineered protocols.

## Development

The integration is located in `custom_components/gree_versati_extended`. Run the
test suite from the repository root with:

```bash
python -m pytest -q
```

The tests cover protocol encoding/decoding, request-format fallback, UDP request
handling and retry behavior, and entity value conversion. They use mocked UDP
responses, so no live heat pump is required.
