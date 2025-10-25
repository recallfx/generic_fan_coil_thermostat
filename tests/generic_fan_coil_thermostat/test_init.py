"""Test the Generic Fan Coil Thermostat component setup."""

from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_ON
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.generic_fan_coil_thermostat import (
    async_setup,
    async_unload_entry,
    async_update_options,
)
from custom_components.generic_fan_coil_thermostat.const import DOMAIN


async def test_async_setup(hass: HomeAssistant):
    """Test the component gets setup."""
    assert await async_setup(hass, {})
    assert DOMAIN in hass.data


async def test_async_setup_entry(hass: HomeAssistant):
    """Test setting up entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            "current_temperature_entity_id": "sensor.temp",
            "fan_entity_id": "fan.test",
            "cooling_switches": ["switch.cool"],
            "heating_switches": ["switch.heat"],
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temp", "20")
    hass.states.async_set("fan.test", STATE_ON)
    hass.states.async_set("switch.cool", STATE_ON)
    hass.states.async_set("switch.heat", STATE_ON)

    # Use async_setup_component which properly sets up the integration
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    assert entry.entry_id in hass.data[DOMAIN]


async def test_async_setup_entry_with_options(hass: HomeAssistant):
    """Test setting up entry with options."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            "current_temperature_entity_id": "sensor.temp",
            "fan_entity_id": "fan.test",
        },
        options={
            "cooling_switches": ["switch.cool1"],
            "min_temp": 16.0,
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temp", "20")
    hass.states.async_set("fan.test", STATE_ON)
    hass.states.async_set("switch.cool1", STATE_ON)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    # Options should override data
    data = hass.data[DOMAIN][entry.entry_id]
    assert data["cooling_switches"] == ["switch.cool1"]
    assert data["min_temp"] == 16.0


async def test_async_unload_entry(hass: HomeAssistant):
    """Test unloading entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            "current_temperature_entity_id": "sensor.temp",
            "fan_entity_id": "fan.test",
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temp", "20")
    hass.states.async_set("fan.test", STATE_ON)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()
    assert entry.entry_id in hass.data[DOMAIN]

    assert await async_unload_entry(hass, entry)
    await hass.async_block_till_done()
    assert entry.entry_id not in hass.data[DOMAIN]


async def test_async_update_options(hass: HomeAssistant):
    """Test updating options triggers reload."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Thermostat",
        data={
            "current_temperature_entity_id": "sensor.temp",
            "fan_entity_id": "fan.test",
        },
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.temp", "20")
    hass.states.async_set("fan.test", STATE_ON)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    # Update options should trigger reload
    await async_update_options(hass, entry)
    await hass.async_block_till_done()
