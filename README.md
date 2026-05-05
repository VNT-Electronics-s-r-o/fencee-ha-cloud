# fencee-ha-cloud

Home Assistant custom integration for Fencee cloud monitoring.

## Configuration

When adding the integration, provide:

- `name`: Friendly name shown in Home Assistant.
- `device_type`: Device type (MC20, EDC) — determines which sensors are created.
- `brand`: `fencee` or `voss`.
- `token`: Cloud API token.
- `mac`: Device MAC address.
- `update_interval`: Polling interval in seconds (60-86400, where 60 is the minimum).

### Supported Device Types

- `MC20`: Creates only voltageFence, voltageBattery, voltageFenceLowTreshold, signal, createdAt, and fault sensors.
- `EDC`: Creates all available sensors (full set).

### Supported MAC formats

The config flow validates these MAC formats:

- `aa:bb:cc:dd:ee:ff`
- `aa-bb-cc-dd-ee-ff`
- `aabbccddeeff`

## Sensors

The integration creates a fixed set of sensors:

- `createdAt` (shown as normal timestamp)
- `voltageFence`
- `voltageBattery`
- `energyFence`
- `impedance`
- `voltageFenceLowTreshold`
- `signal`
- `powerOutput`

This ensures entities are created consistently even when some fields are temporarily missing in API responses.

## Binary Sensors

The integration also creates binary sensors for fault states:

- `hasFaults`
- all keys from `faults.*` payload section

These entities use problem semantics in Home Assistant and switch on/off based on current alarm values.

## API Error Handling

The integration refreshes data using Home Assistant `DataUpdateCoordinator`.
Polling interval is configurable during setup with minimum 60 seconds.
Both sensor and binary sensor entities use one shared coordinator, so there is only one API call per refresh interval.

- HTTP errors (`4xx`/`5xx`) are handled as update failures.
- Connection problems and invalid JSON responses are handled as update failures.
- Home Assistant keeps existing entities and retries on the next polling interval.
