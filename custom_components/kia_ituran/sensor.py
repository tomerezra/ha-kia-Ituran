"""Sensors: one per DiagnosticValues code returned by the API."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfLength
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import KiaIturanConfigEntry
from .const import DOMAIN
from .coordinator import KiaIturanCoordinator

KNOWN: dict[str, dict[str, Any]] = {
    "2334": {
        "name": "Battery",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "2229": {
        "name": "Range",
        "unit": UnitOfLength.KILOMETERS,
        "device_class": SensorDeviceClass.DISTANCE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "2227": {"name": "Charging AC mode"},
    "2291": {"name": "Time remaining for charge"},
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: KiaIturanConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    known: set[str] = set()

    @callback
    def _add_new() -> None:
        codes = [c for c in coordinator.data if c not in known]
        if not codes:
            return
        known.update(codes)
        async_add_entities(KiaIturanSensor(coordinator, entry, c) for c in codes)

    _add_new()
    entry.async_on_unload(coordinator.async_add_listener(_add_new))


class KiaIturanSensor(CoordinatorEntity[KiaIturanCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KiaIturanCoordinator,
        entry: KiaIturanConfigEntry,
        code: str,
    ) -> None:
        super().__init__(coordinator)
        self._code = code
        info = KNOWN.get(code, {})
        self._attr_unique_id = f"{entry.entry_id}_{code}"
        self._attr_name = info.get("name") or coordinator.data[code]["name"]
        self._attr_native_unit_of_measurement = info.get("unit")
        self._attr_device_class = info.get("device_class")
        self._attr_state_class = info.get("state_class")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Kia EV",
            manufacturer="Kia / Ituran",
        )

    @property
    def available(self) -> bool:
        return super().available and self._code in self.coordinator.data

    @property
    def native_value(self) -> Any:
        return self.coordinator.data.get(self._code, {}).get("value")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        item = self.coordinator.data.get(self._code, {})
        return {
            "code": self._code,
            "reported_at": item.get("time"),
            "label": item.get("label"),
        }
