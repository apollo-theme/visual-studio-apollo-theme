#!/usr/bin/env python3
"""Validate the standalone Apollo Visual Studio theme repository."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALETTE_SHA256 = "550f8c36cf4ef6ac99551541d1fe9554f77d563fa1e7c129a6a82583321d61ef"
ARGB = re.compile(r"^[0-9A-F]{8}$")
REQUIRED_CATEGORIES = {"Environment", "Text Editor", "Command Window", "Output Window"}


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


def main() -> int:
    palette_path = ROOT / "palette" / "apollo.json"
    digest = hashlib.sha256(palette_path.read_bytes()).hexdigest()
    if digest != PALETTE_SHA256:
        fail(f"palette snapshot differs from canonical SHA-256: {digest}")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate.py"), "--check"], cwd=ROOT, check=True)
    palette = json.loads(palette_path.read_text(encoding="utf-8"))
    theme_path = ROOT / "themes" / "Apollo.vstheme"
    root = ET.parse(theme_path).getroot()
    if root.tag != "Themes":
        fail("root element must be Themes")
    themes = root.findall("Theme")
    if len(themes) != 1:
        fail("theme file must contain exactly one Theme")
    theme = themes[0]
    if theme.attrib.get("Name") != "Apollo" or theme.attrib.get("MinVSVersion") != "17.0":
        fail("Theme metadata must identify Apollo for Visual Studio 2022+")

    categories = category_map(theme)
    missing = REQUIRED_CATEGORIES - categories.keys()
    if missing:
        fail(f"missing required Visual Studio categories: {sorted(missing)}")
    if len(categories["Environment"].findall("Color")) < 55:
        fail("Environment category is not useful enough")
    editor = color_map(categories["Text Editor"])
    if len(editor) < 35:
        fail("Text Editor category is not useful enough")

    expected = {
        "Plain Text": ("Foreground", "FFCFBC97"),
        "Syntax Error": ("Foreground", "FFFB4934"),
        "Warning": ("Foreground", "FFFABD2F"),
        "Information": ("Foreground", "FF83A598"),
        "Track Changes after save": ("Foreground", "FFB8BB26"),
        "Selected Text": ("Background", "FF3C3836"),
    }
    for name, (channel, value) in expected.items():
        if name not in editor or source(editor[name], channel) != value:
            fail(f"{name} {channel} must be {value}")

    for element in root.findall(".//*[@Source]"):
        value = element.attrib["Source"].upper()
        if not ARGB.fullmatch(value):
            fail(f"invalid CT_RAW source: {value}")
        if element.attrib.get("Type") != "CT_RAW":
            fail(f"all generated colors must use CT_RAW, got {element.attrib.get('Type')}")
        if value == "FF665C54":
            fail("restricted ANSI bright black must not be used in Visual Studio UI/editor text")

    if palette["colors"]["foreground"] != "#cfbc97" or palette["colors"]["accent"] != "#fabd2f":
        fail("palette required foreground/accent values changed")

    print(
        f"validated palette snapshot, {len(categories['Environment'].findall('Color'))} environment colors, "
        f"{len(editor)} editor colors, and {len(root.findall('.//*[@Source]'))} XML color channels"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, ET.ParseError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"check failed: {error}", file=sys.stderr)
        raise SystemExit(1)
