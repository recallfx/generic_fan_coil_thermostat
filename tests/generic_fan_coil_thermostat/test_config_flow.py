"""Test the Generic Fan Coil Thermostat config flow."""

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.const import STATE_ON

from custom_components.generic_fan_coil_thermostat.const import (
    DOMAIN,
    CONF_CURRENT_TEMPERATURE_ENTITY_ID,
    CONF_FAN_ENTITY_ID,
    CONF_COOLING_SWITCHES,
    CONF_HEATING_SWITCHES,
    CONF_MIN_TEMP,
    CONF_MAX_TEMP,
    CONF_TARGET_TEMP,
    CONF_TEMP_STEP,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    DEFAULT_TARGET_TEMP,
    DEFAULT_TEMP_STEP,
)


async def test_user_flow_minimum_config(hass: HomeAssistant):
    """Test we get the form and can create an entry with minimum config."""
    # Set up entities
    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_ON)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
            CONF_COOLING_SWITCHES: [],
            CONF_HEATING_SWITCHES: [],
            CONF_MIN_TEMP: DEFAULT_MIN_TEMP,
            CONF_MAX_TEMP: DEFAULT_MAX_TEMP,
            CONF_TARGET_TEMP: DEFAULT_TARGET_TEMP,
            CONF_TEMP_STEP: DEFAULT_TEMP_STEP,
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Generic Fan Coil Thermostat - fan.test_fan"
    assert result["data"] == {
        CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
        CONF_FAN_ENTITY_ID: "fan.test_fan",
        CONF_COOLING_SWITCHES: [],
        CONF_HEATING_SWITCHES: [],
        CONF_MIN_TEMP: DEFAULT_MIN_TEMP,
        CONF_MAX_TEMP: DEFAULT_MAX_TEMP,
        CONF_TARGET_TEMP: DEFAULT_TARGET_TEMP,
        CONF_TEMP_STEP: DEFAULT_TEMP_STEP,
    }


async def test_user_flow_with_switches(hass: HomeAssistant):
    """Test config flow with cooling and heating switches."""
    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_ON)
    hass.states.async_set("switch.cool1", STATE_ON)
    hass.states.async_set("switch.cool2", STATE_ON)
    hass.states.async_set("switch.heat1", STATE_ON)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
            CONF_COOLING_SWITCHES: ["switch.cool1", "switch.cool2"],
            CONF_HEATING_SWITCHES: ["switch.heat1"],
            CONF_MIN_TEMP: 16.0,
            CONF_MAX_TEMP: 28.0,
            CONF_TARGET_TEMP: 21.0,
            CONF_TEMP_STEP: 1.0,
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_COOLING_SWITCHES] == ["switch.cool1", "switch.cool2"]
    assert result["data"][CONF_HEATING_SWITCHES] == ["switch.heat1"]
    assert result["data"][CONF_MIN_TEMP] == 16.0
    assert result["data"][CONF_MAX_TEMP] == 28.0


async def test_user_flow_temperature_entity_not_found(hass: HomeAssistant):
    """Test error when temperature entity not found."""
    hass.states.async_set("fan.test_fan", STATE_ON)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.nonexistent",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {CONF_CURRENT_TEMPERATURE_ENTITY_ID: "entity_not_found"}


async def test_user_flow_fan_entity_not_found(hass: HomeAssistant):
    """Test error when fan entity not found."""
    hass.states.async_set("sensor.temperature", "20")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.nonexistent",
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {CONF_FAN_ENTITY_ID: "entity_not_found"}


async def test_user_flow_duplicate_entry(hass: HomeAssistant):
    """Test duplicate entry is rejected."""
    hass.states.async_set("sensor.temperature", "20")
    hass.states.async_set("fan.test_fan", STATE_ON)

    # Create first entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Try to create duplicate
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temperature",
            CONF_FAN_ENTITY_ID: "fan.test_fan",
        },
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow(hass: HomeAssistant):
    """Test options flow."""
    from homeassistant.config_entries import ConfigEntry

    entry = ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Test",
        data={
            CONF_CURRENT_TEMPERATURE_ENTITY_ID: "sensor.temp",
            CONF_FAN_ENTITY_ID: "fan.test",
            CONF_COOLING_SWITCHES: ["switch.cool1"],
            CONF_MIN_TEMP: DEFAULT_MIN_TEMP,
        },
        options={},
        source="user",
        entry_id="test_entry",
        unique_id="test_unique",
        discovery_keys={},
    )

    hass.config_entries._entries[entry.entry_id] = entry

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_COOLING_SWITCHES: ["switch.cool2"],
            CONF_HEATING_SWITCHES: ["switch.heat1"],
            CONF_MIN_TEMP: 18.0,
            CONF_MAX_TEMP: 26.0,
            CONF_TARGET_TEMP: 22.0,
            CONF_TEMP_STEP: 0.5,
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_COOLING_SWITCHES: ["switch.cool2"],
        CONF_HEATING_SWITCHES: ["switch.heat1"],
        CONF_MIN_TEMP: 18.0,
        CONF_MAX_TEMP: 26.0,
        CONF_TARGET_TEMP: 22.0,
        CONF_TEMP_STEP: 0.5,
    }
