"""Ituran GetElectricData client."""
from __future__ import annotations

import asyncio
import re
import xml.etree.ElementTree as ET
from typing import Any

import aiohttp

from .const import API_URL, USER_AGENT

_LABEL_RE = re.compile(r"^(?:Electric Data - )?(?P<name>.*?) - (?P<code>[0-9]{1,})$")


class CannotConnect(Exception):
    """Network or parsing failure."""


class InvalidAuth(Exception):
    """The API returned a non-OK ReturnCode."""


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _convert(value: str | None) -> Any:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def parse_response(body: bytes) -> dict[str, dict[str, Any]]:
    """Parse the XML into {code: {name, value, time, label}}."""
    try:
        root = ET.fromstring(body)
    except ET.ParseError as err:
        raise CannotConnect("Invalid XML response") from err

    code_ok = None
    for el in root.iter():
        if _local(el.tag) == "ReturnCode":
            code_ok = (el.text or "").strip()
            break
    if code_ok != "OK":
        raise InvalidAuth(f"ReturnCode={code_ok}")

    result: dict[str, dict[str, Any]] = {}
    for el in root.iter():
        if _local(el.tag) != "DiagnosticValues":
            continue
        fields = {_local(c.tag): (c.text or "").strip() for c in el}
        label = fields.get("Label", "")
        match = _LABEL_RE.match(label)
        if not match:
            continue
        result[match["code"]] = {
            "name": match["name"],
            "label": label,
            "value": _convert(fields.get("Value")),
            "time": fields.get("LocTime"),
        }
    return result


async def async_fetch_electric_data(
    session: aiohttp.ClientSession,
    username: str,
    password: str,
    platform_id: str,
) -> dict[str, dict[str, Any]]:
    """Call the API and return parsed data."""
    try:
        async with asyncio.timeout(30):
            async with session.post(
                API_URL,
                data={
                    "UserName": username,
                    "Password": password,
                    "PlatformId": platform_id,
                },
                headers={"User-Agent": USER_AGENT},
            ) as resp:
                resp.raise_for_status()
                body = await resp.read()
    except (aiohttp.ClientError, TimeoutError) as err:
        raise CannotConnect(str(err)) from err
    return parse_response(body)
