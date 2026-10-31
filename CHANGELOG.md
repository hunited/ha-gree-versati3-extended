# Changelog

## 0.1.10 - 2026-10-31

- Grouped the seven core status parameters into one request and Hi/Lo
  temperature registers into pairs.
- Added automatic individual-request fallback for failed or incomplete groups.
- Added GitHub Actions checks for Home Assistant integration validation and
  the Python test suite.

## 0.1.9 - 2026-10-31

- Added heating and cooling icons to the corresponding temperature setpoints.
- Added heat-pump and HVAC icons to the power and operating-mode controls.
- Added descriptive icons to the measured temperature sensors.

## 0.1.8 - 2026-10-30

- Changed the default polling interval to five minutes.
- Added translated operating-mode options, including Hungarian labels.
- Removed sensors that duplicated controls and setpoints.
- Displayed binary sensor values as On/Off or Be/Ki based on the Home Assistant
  language, and displayed the temperature unit as °C or °F.
- Made the Versati series sensor name device-neutral.
