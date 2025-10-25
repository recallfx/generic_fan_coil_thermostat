"""Test the Generic Fan Coil Thermostat climate platform."""

from homeassistant.components.climate import HVACMode, HVACAction
from homeassistant.const import STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.generic_fan_coil_thermostat.const import (
    DOMAIN,
    CONF_CURRENT_TEMPERATURE_ENTITY_ID,
    CONF_FAN_ENTITY_ID,
    CONF_COOLING_SWITCHES,
    CONF_HEATING_SWITCHES,
    CONF_MIN_TEMP,
    CONF_MAX_TEMP,
)


async def test_climate_entity_setup(hass: HomeAssistant):
    """Test climate entity is set up correctly."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_OFF)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    state = hass.states.get("climate.generic_fan_coil_thermostat")
    assert state is not None
    assert state.state == HVACMode.OFF


async def test_climate_attributes(hass: HomeAssistant):
    """Test climate entity attributes."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
            CONF_MIN_TEMP: 16.0,
            CONF_MAX_TEMP: 28.0,
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_OFF)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    state = hass.states.get("climate.generic_fan_coil_thermostat")
    assert state.attributes["min_temp"] == 16.0
    assert state.attributes["max_temp"] == 28.0
    assert state.attributes["current_temperature"] == 20.0
    assert state.attributes["fan_mode"] == "auto"


async def test_hvac_modes_with_cooling_only(hass: HomeAssistant):
    """Test HVAC modes when only cooling switches are configured."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
            CONF_COOLING_SWITCHES: ["switch.cool1"],
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_OFF)
    hass.states.async_set("switch.cool1", STATE_OFF)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    state = hass.states.get("climate.generic_fan_coil_thermostat")
    assert HVACMode.OFF in state.attributes["hvac_modes"]
    assert HVACMode.COOL in state.attributes["hvac_modes"]
    assert HVACMode.HEAT not in state.attributes["hvac_modes"]


async def test_hvac_modes_with_heating_only(hass: HomeAssistant):
    """Test HVAC modes when only heating switches are configured."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
            CONF_HEATING_SWITCHES: ["switch.heat1"],
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_OFF)
    hass.states.async_set("switch.heat1", STATE_OFF)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    state = hass.states.get("climate.generic_fan_coil_thermostat")
    assert HVACMode.OFF in state.attributes["hvac_modes"]
    assert HVACMode.HEAT in state.attributes["hvac_modes"]
    assert HVACMode.COOL not in state.attributes["hvac_modes"]


async def test_set_temperature(hass: HomeAssistant):
    """Test setting target temperature."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_OFF)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    await hass.services.async_call(
        "climate",
        "set_temperature",
        {
            "entity_id": "climate.generic_fan_coil_thermostat",
            "temperature": 25.0,
        },
        blocking=True,
    )

    state = hass.states.get("climate.generic_fan_coil_thermostat")
    assert state.attributes["temperature"] == 25.0


async def test_set_hvac_mode_off(hass: HomeAssistant):
    """Test setting hvac mode to off."""
    # Setup fan and switch components for service calls
    await async_setup_component(hass, "fan", {})
    await async_setup_component(hass, "switch", {})

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
            CONF_COOLING_SWITCHES: ["switch.cool1"],
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_OFF)
    hass.states.async_set("switch.cool1", STATE_OFF)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    # Turn on cooling first
    await hass.services.async_call(
        "climate",
        "set_hvac_mode",
        {
            "entity_id": "climate.generic_fan_coil_thermostat",
            "hvac_mode": HVACMode.COOL,
        },
        blocking=True,
    )

    # Then turn off
    await hass.services.async_call(
        "climate",
        "set_hvac_mode",
        {
            "entity_id": "climate.generic_fan_coil_thermostat",
            "hvac_mode": HVACMode.OFF,
        },
        blocking=True,
    )

    state = hass.states.get("climate.generic_fan_coil_thermostat")
    assert state.state == HVACMode.OFF
    assert state.attributes["hvac_action"] == HVACAction.OFF


async def test_set_fan_mode(hass: HomeAssistant):
    """Test setting fan mode."""
    # Setup fan component for service calls
    await async_setup_component(hass, "fan", {})

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_OFF)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    await hass.services.async_call(
        "climate",
        "set_fan_mode",
        {
            "entity_id": "climate.generic_fan_coil_thermostat",
            "fan_mode": "low",
        },
        blocking=True,
    )

    state = hass.states.get("climate.generic_fan_coil_thermostat")
    assert state.attributes["fan_mode"] == "low"


async def test_cooling_triggers_action(hass: HomeAssistant):
    """Test cooling action is triggered when temperature is above target."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
            CONF_COOLING_SWITCHES: ["switch.cool1"],
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temperature", "24")
    hass.states.async_set("fan.test_fan", STATE_OFF)
    hass.states.async_set("switch.cool1", STATE_OFF)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    # Set to cooling mode
    await hass.services.async_call(
        "climate",
        "set_hvac_mode",
        {
            "entity_id": "climate.generic_fan_coil_thermostat",
            "hvac_mode": HVACMode.COOL,
        },
        blocking=True,
    )

    state = hass.states.get("climate.generic_fan_coil_thermostat")
    # Should be cooling since temp (24) > target (22)
    assert state.attributes["hvac_action"] == HVACAction.COOLING


async def test_heating_triggers_action(hass: HomeAssistant):
    """Test heating action is triggered when temperature is below target."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
            CONF_HEATING_SWITCHES: ["switch.heat1"],
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_OFF)
    hass.states.async_set("switch.heat1", STATE_OFF)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    # Set to heating mode
    await hass.services.async_call(
        "climate",
        "set_hvac_mode",
        {
            "entity_id": "climate.generic_fan_coil_thermostat",
            "hvac_mode": HVACMode.HEAT,
        },
        blocking=True,
    )

    state = hass.states.get("climate.generic_fan_coil_thermostat")
    # Should be heating since temp (20) < target (22)
    assert state.attributes["hvac_action"] == HVACAction.HEATING


async def test_temperature_change_updates_entity(hass: HomeAssistant):
    """Test that temperature sensor changes update the climate entity."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_OFF)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    # Change temperature
    hass.states.async_set("sensor.temperature", "25")
    await hass.async_block_till_done()

    state = hass.states.get("climate.generic_fan_coil_thermostat")
    assert state.attributes["current_temperature"] == 25.0


async def test_turn_on_service(hass: HomeAssistant):
    """Test turn on service defaults to first available mode."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
            CONF_COOLING_SWITCHES: ["switch.cool1"],
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_OFF)
    hass.states.async_set("switch.cool1", STATE_OFF)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    await hass.services.async_call(
        "climate",
        "turn_on",
        {"entity_id": "climate.generic_fan_coil_thermostat"},
        blocking=True,
    )

    state = hass.states.get("climate.generic_fan_coil_thermostat")
    # Should default to cool mode (first available mode)
    assert state.state == HVACMode.COOL


async def test_turn_off_service(hass: HomeAssistant):
    """Test turn off service."""
    # Setup fan component for service calls
    await async_setup_component(hass, "fan", {})

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_OFF)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    await hass.services.async_call(
        "climate",
        "turn_off",
        {"entity_id": "climate.generic_fan_coil_thermostat"},
        blocking=True,
    )

    state = hass.states.get("climate.generic_fan_coil_thermostat")
    assert state.state == HVACMode.OFF
