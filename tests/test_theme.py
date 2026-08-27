from __future__ import annotations

import hashlib
import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate  # noqa: E402


class VisualStudioThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.palette_path = ROOT / "palette" / "apollo.json"
        cls.palette = json.loads(cls.palette_path.read_text(encoding="utf-8"))
        cls.theme_path = ROOT / "themes" / "Apollo.vstheme"
        cls.theme_text = cls.theme_path.read_text(encoding="utf-8")
        cls.root = ET.fromstring(cls.theme_text)

    def test_palette_snapshot_is_canonical(self) -> None:
        digest = hashlib.sha256(self.palette_path.read_bytes()).hexdigest()
        self.assertEqual(
            digest,
            "550f8c36cf4ef6ac99551541d1fe9554f77d563fa1e7c129a6a82583321d61ef",
        )

    def test_generated_theme_is_current(self) -> None:
        self.assertEqual(self.theme_text, generate.render_theme(self.palette))

    def test_current_theme_structure_and_categories(self) -> None:
        self.assertEqual(self.root.tag, "Themes")
        theme = self.root.find("Theme")
        self.assertIsNotNone(theme)
        assert theme is not None
        self.assertEqual(theme.attrib["Name"], "Apollo")
        self.assertEqual(theme.attrib["MinVSVersion"], "17.0")
        categories = {category.attrib["Name"] for category in theme.findall("Category")}
        self.assertTrue(
            {"Environment", "Text Editor", "Command Window", "Output Window"}.issubset(categories),
            categories,
        )

    def test_editor_status_colors_match_palette(self) -> None:
        theme = self.root.find("Theme")
        assert theme is not None
        text_editor = next(category for category in theme.findall("Category") if category.attrib["Name"] == "Text Editor")
        entries = {color.attrib["Name"]: color for color in text_editor.findall("Color")}

        def foreground(name: str) -> str:
            node = entries[name].find("Foreground")
            assert node is not None
            return node.attrib["Source"]

        self.assertEqual(foreground("Plain Text"), "FFCFBC97")
        self.assertEqual(foreground("Syntax Error"), "FFFB4934")
        self.assertEqual(foreground("Warning"), "FFFABD2F")
        self.assertEqual(foreground("Track Changes after save"), "FFB8BB26")
        self.assertEqual(foreground("Information"), "FF83A598")

    def test_restricted_color_is_not_used_by_visual_studio_theme(self) -> None:
        self.assertNotIn("FF665C54", self.theme_text.upper())

    def test_editor_category_is_useful(self) -> None:
        theme = self.root.find("Theme")
        assert theme is not None
        text_editor = next(category for category in theme.findall("Category") if category.attrib["Name"] == "Text Editor")
        names = {color.attrib["Name"] for color in text_editor.findall("Color")}
        for name in (
            "Comment",
            "Identifier",
            "Keyword",
            "Line Number",
            "Number",
            "Selected Text",
            "String",
            "User Types",
            "Visible White Space",
        ):
            self.assertIn(name, names)
        self.assertGreaterEqual(len(names), 35)


if __name__ == "__main__":
    unittest.main()
