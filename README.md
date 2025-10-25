# Generic Fan Coil Thermostat

A Home Assistant integration that turns a fan and temperature sensor into a smart climate control system. The fan speed adjusts automatically based on how far the room temperature is from your target, and you can wire in switches to control heating or cooling equipment.

## What it does

This creates a standard climate entity (thermostat) that controls an existing fan entity. When the room gets too warm or too cold, it ramps the fan speed up or down to compensate. If you connect switches for heating or cooling equipment (like a boiler relay or heat exchanger), it'll turn those on when needed.

The automatic fan speed control is the main feature—it looks at the temperature gap and picks low, medium, or high speed accordingly. You can also override this and lock the fan to a specific speed if you want.

## Installation

### HACS (recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Generic Fan Coil Thermostat" and install it
3. Restart Home Assistant

### Manual

1. Copy the `custom_components/generic_fan_coil_thermostat` folder into your `config/custom_components` directory
2. Restart Home Assistant

### Setup

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "Generic Fan Coil Thermostat"
3. Pick your temperature sensor and fan entity
4. (Optional) Add switches for cooling or heating equipment
5. (Optional) Adjust temperature limits and defaults

The integration only shows heating/cooling modes if you've configured the corresponding switches. Without any switches, both modes are available for fan-only operation.

## How to use it

The thermostat shows up as a climate entity. Add it to your dashboard with a thermostat card, just like any other climate device.

**Modes:**
- **Off** — Everything stops (fan and switches turn off)
- **Cool** — Keeps temperature at or below target (requires cooling switches, or works fan-only)
- **Heat** — Keeps temperature at or above target (requires heating switches, or works fan-only)

**Fan control:**
- **Auto** — Fan speed adjusts based on temperature difference (recommended)
- **Low/Medium/High** — Fan runs at fixed speed regardless of temperature
- **Off** — Fan stays off even if heating/cooling is active

The switches turn on and off automatically based on whether heating or cooling is needed, independent of fan mode.

## Fan speed thresholds

When in auto mode, the fan speed responds to how far off the temperature is:

**Cooling** (room too warm):
- Less than 0.5°C over target: fan off, cooling switches off
- 0.5°C to 1.5°C over: fan low, cooling switches on
- 1.5°C to 2.5°C over: fan medium, cooling switches on  
- More than 2.5°C over: fan high, cooling switches on

**Heating** (room too cold):
- Less than 0.5°C under target: fan off, heating switches off
- 0.5°C to 1.5°C under: fan low, heating switches on
- 1.5°C to 2.5°C under: fan medium, heating switches on
- More than 2.5°C under: fan high, heating switches on

## What to connect to the switches

The switch inputs are meant for relays or smart switches that control your actual heating/cooling hardware.

**Cooling switches:**
- Heat exchanger valve controls
- Chilled water pump relays
- Air conditioning unit toggles
- Fan coil unit cooling valves

**Heating switches:**
- Boiler or furnace relays
- Heating element controls
- Hot water pump switches  
- Heating valve actuators
- Electric heater toggles

You can connect multiple switches to each input (e.g., one for a pump and one for a valve). They all turn on and off together when that mode activates.

## Requirements

- A fan entity that supports percentage-based speed control
- A temperature sensor entity (any numeric sensor reporting temperature)
- (Optional) Switch entities for controlling heating/cooling equipment

The fan needs to respond to `fan.set_percentage` service calls with values of 33% (low), 66% (medium), and 100% (high).
