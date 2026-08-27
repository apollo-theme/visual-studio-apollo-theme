#!/usr/bin/env python3
"""Generate Apollo.vstheme from the vendored Apollo palette snapshot."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PALETTE_PATH = ROOT / "palette" / "apollo.json"
OUTPUT_PATH = ROOT / "themes" / "Apollo.vstheme"
THEME_GUID = "{895D123B-BC2C-58B5-B006-149BC8F1B5E7}"
ENVIRONMENT_GUID = "{624ED9C3-BDFD-41FA-96C3-7C824EA32E3D}"
TEXT_EDITOR_GUID = "{75A05685-00A8-4DED-BAE5-E7A50BFA929A}"
COMMAND_WINDOW_GUID = "{EE1BE240-4E81-4BEB-8EEA-54322B6B1BF5}"
OUTPUT_WINDOW_GUID = "{9973EFDF-317D-431C-8BC1-5E88CBFD4F7F}"


def argb(color: str, alpha: str = "FF") -> str:
    return alpha + color.removeprefix("#").upper()


def add_color(
    category: ET.Element,
    name: str,
    *,
    foreground: str | None = None,
    background: str | None = None,
    bold: bool = False,
) -> None:
    color = ET.SubElement(category, "Color", {"Name": name})
    if background is not None:
        ET.SubElement(color, "Background", {"Type": "CT_RAW", "Source": argb(background)})
    if foreground is not None:
        attributes = {"Type": "CT_RAW", "Source": argb(foreground)}
        if bold:
            attributes["FontIsBold"] = "Yes"
        ET.SubElement(color, "Foreground", attributes)


def build_theme(palette: dict[str, Any]) -> ET.Element:
    c = palette["colors"]
    root = ET.Element("Themes")
    theme = ET.SubElement(
        root,
        "Theme",
        {"Name": "Apollo", "GUID": THEME_GUID, "MinVSVersion": "17.0"},
    )

    environment = ET.SubElement(theme, "Category", {"Name": "Environment", "GUID": ENVIRONMENT_GUID})
    environment_colors: list[tuple[str, str | None, str | None]] = [
        ("EnvironmentBackground", c["foreground"], c["background"]),
        ("EnvironmentForeground", c["foreground"], None),
        ("Window", c["foreground"], c["background"]),
        ("WindowText", c["foreground"], None),
        ("Control", c["foreground"], c["surface"]),
        ("ControlText", c["foreground"], None),
        ("ControlDark", None, c["background"]),
        ("ControlLight", None, c["surface"]),
        ("ControlLightLight", None, c["surfaceHover"]),
        ("ControlOutline", None, c["selection"]),
        ("GrayText", c["foregroundInactive"], None),
        ("Highlight", c["foregroundBright"], c["selection"]),
        ("HighlightText", c["foregroundBright"], None),
        ("InactiveCaption", c["foregroundInactive"], c["background"]),
        ("InactiveCaptionText", c["foregroundInactive"], None),
        ("InactiveBorder", None, c["surface"]),
        ("ActiveBorder", None, c["accent"]),
        ("CommandBarMenuBackgroundGradientBegin", None, c["surface"]),
        ("CommandBarMenuBackgroundGradientEnd", None, c["surface"]),
        ("CommandBarMenuBorder", None, c["selection"]),
        ("CommandBarMenuItemMouseOver", c["foregroundBright"], c["selection"]),
        ("CommandBarTextActive", c["foregroundBright"], None),
        ("CommandBarTextInactive", c["foregroundInactive"], None),
        ("CommandBarToolbarBackground", None, c["background"]),
        ("CommandBarToolbarBorder", None, c["surface"]),
        ("ToolWindowBackground", c["foreground"], c["background"]),
        ("ToolWindowText", c["foreground"], None),
        ("ToolWindowBorder", None, c["surface"]),
        ("ToolWindowTabSelectedActive", c["foregroundBright"], c["surface"]),
        ("ToolWindowTabSelectedInactive", c["foregroundSecondary"], c["surface"]),
        ("ToolWindowTabUnselected", c["foregroundInactive"], c["background"]),
        ("ToolWindowTabMouseOver", c["foregroundBright"], c["surfaceHover"]),
        ("FileTabSelectedBackground", c["foregroundBright"], c["background"]),
        ("FileTabSelectedText", c["foregroundBright"], None),
        ("FileTabInactiveBackground", c["foregroundInactive"], c["background"]),
        ("FileTabInactiveText", c["foregroundInactive"], None),
        ("FileTabHotBackground", c["foregroundBright"], c["surfaceHover"]),
        ("FileTabHotText", c["foregroundBright"], None),
        ("FileTabChannel", None, c["surface"]),
        ("StatusBar", c["foregroundSecondary"], c["surface"]),
        ("StatusBarText", c["foregroundSecondary"], None),
        ("StatusBarHighlight", c["background"], c["accent"]),
        ("StatusBarHighlightText", c["background"], None),
        ("InfoBarBackground", c["background"], c["info"]),
        ("InfoBarText", c["background"], None),
        ("SearchControlBackground", c["foreground"], c["surface"]),
        ("SearchControlBorder", None, c["selection"]),
        ("SearchControlFocusedBackground", c["foregroundBright"], c["surfaceHover"]),
        ("SearchControlFocusedBorder", None, c["accent"]),
        ("SearchControlText", c["foreground"], None),
        ("SearchMatch", c["background"], c["accent"]),
        ("DropDownBackground", c["foreground"], c["surface"]),
        ("DropDownBorder", None, c["selection"]),
        ("DropDownMouseOverBackground", c["foregroundBright"], c["selection"]),
        ("DropDownText", c["foreground"], None),
        ("ButtonFace", c["background"], c["accent"]),
        ("ButtonText", c["background"], None),
        ("ButtonMouseOverBackground", c["background"], c["foregroundBright"]),
        ("ButtonMouseOverText", c["background"], None),
        ("ButtonDisabledBackground", c["foregroundInactive"], c["surface"]),
        ("ButtonDisabledText", c["foregroundInactive"], None),
        ("NotificationInfo", c["info"], c["surface"]),
        ("NotificationWarning", c["accent"], c["surface"]),
        ("NotificationError", c["danger"], c["surface"]),
    ]
    for name, foreground, background in environment_colors:
        add_color(environment, name, foreground=foreground, background=background)

    editor = ET.SubElement(theme, "Category", {"Name": "Text Editor", "GUID": TEXT_EDITOR_GUID})
    editor_colors: list[tuple[str, str | None, str | None, bool]] = [
        ("Plain Text", c["foreground"], c["background"], False),
        ("Selected Text", c["foregroundBright"], c["selection"], False),
        ("Inactive Selected Text", c["foregroundSecondary"], c["selection"], False),
        ("Line Number", c["foregroundInactive"], c["background"], False),
        ("Visible White Space", c["selection"], c["background"], False),
        ("Indicator Margin", None, c["background"], False),
        ("Comment", c["foregroundInactive"], c["background"], False),
        ("Identifier", c["foreground"], c["background"], False),
        ("Keyword", c["danger"], c["background"], False),
        ("String", c["success"], c["background"], False),
        ("Number", c["magenta"], c["background"], False),
        ("Operator", c["foregroundSecondary"], c["background"], False),
        ("Preprocessor Keyword", c["magenta"], c["background"], False),
        ("User Types", c["accent"], c["background"], False),
        ("User Types (Delegates)", c["accent"], c["background"], False),
        ("User Types (Enums)", c["accent"], c["background"], False),
        ("User Types (Interfaces)", c["accent"], c["background"], False),
        ("User Types (Type parameters)", c["magenta"], c["background"], False),
        ("Class Name", c["accent"], c["background"], False),
        ("Struct Name", c["accent"], c["background"], False),
        ("Interface Name", c["accent"], c["background"], False),
        ("Enum Name", c["accent"], c["background"], False),
        ("Delegate Name", c["accent"], c["background"], False),
        ("Type Parameter Name", c["magenta"], c["background"], False),
        ("Namespace Name", c["cyan"], c["background"], False),
        ("Method Name", c["accent"], c["background"], False),
        ("Extension Method Name", c["accent"], c["background"], False),
        ("Property Name", c["info"], c["background"], False),
        ("Field Name", c["info"], c["background"], False),
        ("Local Name", c["foreground"], c["background"], False),
        ("Parameter Name", c["foregroundSecondary"], c["background"], False),
        ("Enum Member Name", c["magenta"], c["background"], False),
        ("Event Name", c["cyan"], c["background"], False),
        ("Constant Name", c["magenta"], c["background"], False),
        ("Label Name", c["cyan"], c["background"], False),
        ("XML Doc Comment - Text", c["foregroundInactive"], c["background"], False),
        ("XML Doc Comment - Name", c["cyan"], c["background"], False),
        ("XML Doc Comment - Attribute Name", c["accent"], c["background"], False),
        ("XML Doc Comment - Attribute Quotes", c["foregroundSecondary"], c["background"], False),
        ("CSS Property Name", c["info"], c["background"], False),
        ("CSS Selector", c["cyan"], c["background"], False),
        ("HTML Attribute", c["accent"], c["background"], False),
        ("HTML Element Name", c["cyan"], c["background"], False),
        ("JSON Property Name", c["info"], c["background"], False),
        ("Current Statement", c["background"], c["accent"], False),
        ("Breakpoint (Enabled)", c["foregroundBright"], c["danger"], False),
        ("Syntax Error", c["danger"], c["background"], True),
        ("Warning", c["accent"], c["background"], False),
        ("Information", c["info"], c["background"], False),
        ("Track Changes before save", c["accent"], c["background"], False),
        ("Track Changes after save", c["success"], c["background"], False),
        ("Brace Matching (Highlight)", c["accent"], c["selection"], True),
        ("Find Match Highlight", c["background"], c["accent"], False),
        ("Code Snippet Field", c["foregroundBright"], c["selection"], False),
        ("URL Hyperlink", c["info"], c["background"], False),
    ]
    for name, foreground, background, bold in editor_colors:
        add_color(editor, name, foreground=foreground, background=background, bold=bold)

    for name, guid in (("Command Window", COMMAND_WINDOW_GUID), ("Output Window", OUTPUT_WINDOW_GUID)):
        category = ET.SubElement(theme, "Category", {"Name": name, "GUID": guid})
        add_color(category, "Plain Text", foreground=c["foreground"], background=c["background"])
        add_color(category, "Selected Text", foreground=c["foregroundBright"], background=c["selection"])
        add_color(category, "Error", foreground=c["danger"], background=c["background"])
        add_color(category, "Warning", foreground=c["accent"], background=c["background"])
        add_color(category, "Information", foreground=c["info"], background=c["background"])

    return root


def render_theme(palette: dict[str, Any]) -> str:
    root = build_theme(palette)
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding="unicode", short_empty_elements=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if Apollo.vstheme is stale")
    args = parser.parse_args()
    palette = json.loads(PALETTE_PATH.read_text(encoding="utf-8"))
    expected = render_theme(palette)

    if args.check:
        actual = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if actual != expected:
            print(f"{OUTPUT_PATH.relative_to(ROOT)} is stale; run python3 scripts/generate.py", file=sys.stderr)
            return 1
        print(f"{OUTPUT_PATH.relative_to(ROOT)} is current")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(expected, encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
