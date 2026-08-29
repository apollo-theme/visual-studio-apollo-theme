#!/usr/bin/env python3
"""Validate both standalone Apollo Visual Studio theme variants."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALETTE_SHA256 = {
    "apollo": "550f8c36cf4ef6ac99551541d1fe9554f77d563fa1e7c129a6a82583321d61ef",
    "apollo-light": "b0dbdeb719ed1931c424e9590562689325ecac1609e2fed6406ec5c4d3dc5763",
}
VARIANTS = (
    ("apollo", "dark", "Apollo", "{895D123B-BC2C-58B5-B006-149BC8F1B5E7}", ROOT / "palette" / "apollo.json", ROOT / "themes" / "Apollo.vstheme"),
    ("apollo-light", "light", "Apollo Light", "{28E5D943-7F6B-5B87-B6F0-9AEF73CD4F34}", ROOT / "palette" / "apollo-light.json", ROOT / "themes" / "Apollo Light.vstheme"),
)
ARGB = re.compile(r"^[0-9A-F]{8}$")
REQUIRED_CATEGORIES = {
    "Environment": "{624ED9C3-BDFD-41FA-96C3-7C824EA32E3D}",
    "Text Editor": "{75A05685-00A8-4DED-BAE5-E7A50BFA929A}",
    "Command Window": "{EE1BE240-4E81-4BEB-8EEA-54322B6B1BF5}",
    "Output Window": "{9973EFDF-317D-431C-8BC1-5E88CBFD4F7F}",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def category_map(theme: ET.Element) -> dict[str, ET.Element]:
    return {category.attrib["Name"]: category for category in theme.findall("Category")}


def color_map(category: ET.Element) -> dict[str, ET.Element]:
    return {color.attrib["Name"]: color for color in category.findall("Color")}


def source(node: ET.Element, child_name: str) -> str:
    child = node.find(child_name)
    if child is None:
        fail(f"{node.attrib.get('Name')} has no {child_name}")
    assert child is not None
    return child.attrib["Source"]


def argb(color: str) -> str:
    return "FF" + color.removeprefix("#").upper()


def validate_variant(
    variant_id: str,
    appearance: str,
    name: str,
    guid: str,
    palette_path: Path,
    theme_path: Path,
) -> tuple[int, int, int]:
    palette_bytes = palette_path.read_bytes()
    digest = hashlib.sha256(palette_bytes).hexdigest()
    if digest != PALETTE_SHA256[variant_id]:
        fail(f"{palette_path.relative_to(ROOT)} differs from canonical SHA-256: {digest}")
    palette = json.loads(palette_bytes)
    if (palette.get("id"), palette.get("appearance")) != (variant_id, appearance):
        fail(f"{palette_path.name} has incorrect variant semantics")

    root = ET.parse(theme_path).getroot()
    if root.tag != "Themes" or len(root.findall("Theme")) != 1:
        fail(f"{theme_path.name} must contain exactly one Theme")
    theme = root.find("Theme")
    assert theme is not None
    if theme.attrib != {"Name": name, "GUID": guid, "MinVSVersion": "17.0"}:
        fail(f"{theme_path.name} metadata is incorrect: {theme.attrib}")

    categories = category_map(theme)
    if set(categories) != set(REQUIRED_CATEGORIES):
        fail(f"{theme_path.name} categories are incorrect: {sorted(categories)}")
    for category_name, category_guid in REQUIRED_CATEGORIES.items():
        if categories[category_name].attrib.get("GUID") != category_guid:
            fail(f"{theme_path.name} changed {category_name} category GUID")
    if len(categories["Environment"].findall("Color")) < 55:
        fail(f"{theme_path.name} Environment category is incomplete")
    editor = color_map(categories["Text Editor"])
    if len(editor) < 35:
        fail(f"{theme_path.name} Text Editor category is incomplete")

    colors = palette["colors"]
    expected = {
        "Plain Text": ("Foreground", colors["foreground"]),
        "Syntax Error": ("Foreground", colors["danger"]),
        "Warning": ("Foreground", colors["accent"]),
        "Information": ("Foreground", colors["info"]),
        "Track Changes after save": ("Foreground", colors["success"]),
        "Selected Text": ("Background", colors["selection"]),
    }
    for color_name, (channel, value) in expected.items():
        if color_name not in editor or source(editor[color_name], channel) != argb(value):
            fail(f"{theme_path.name}: {color_name} {channel} must be {argb(value)}")

    for element in root.findall(".//*[@Source]"):
        value = element.attrib["Source"].upper()
        if not ARGB.fullmatch(value):
            fail(f"{theme_path.name} has invalid CT_RAW source: {value}")
        if element.attrib.get("Type") != "CT_RAW":
            fail(f"{theme_path.name} has non-CT_RAW generated color")
        if variant_id == "apollo" and value == "FF665C54":
            fail("restricted dark ANSI bright black appears in Visual Studio UI/editor text")

    return (
        len(categories["Environment"].findall("Color")),
        len(editor),
        len(root.findall(".//*[@Source]")),
    )


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate.py"), "--check"], cwd=ROOT, check=True)
    if len({variant[3] for variant in VARIANTS}) != len(VARIANTS):
        fail("theme GUIDs must be unique")
    counts = [validate_variant(*variant) for variant in VARIANTS]
    print(
        "validated two palette snapshots and Visual Studio variants; "
        + ", ".join(
            f"{variant[0]}={environment} environment/{editor} editor/{channels} channels"
            for variant, (environment, editor, channels) in zip(VARIANTS, counts, strict=True)
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, OSError, ET.ParseError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"check failed: {error}", file=sys.stderr)
        raise SystemExit(1)
