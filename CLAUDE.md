# Apollo Theme for Visual Studio

This standalone repository ships a native Visual Studio 2022+ `.vstheme`. `palette/apollo.json` is an exact canonical snapshot; never hand-edit `themes/Apollo.vstheme` or copy obsolete colors from another editor theme.

## Commands

- Regenerate: `python3 scripts/generate.py`
- Determinism check: `python3 scripts/generate.py --check`
- Repository checks: `python3 scripts/check.py`
- All tests: `python3 -m unittest discover -s tests -v`
- One named test: `python3 -m unittest tests.test_theme.VisualStudioThemeTests.test_editor_status_colors_match_palette`
- XML schema validation: `xmllint --noout --schema schemas/vstheme.xsd themes/Apollo.vstheme`
- Windows native validation: `pwsh -File scripts/validate.ps1`

## Invariants

- Generate every color from `palette/apollo.json`.
- Keep foreground `#cfbc97`, accent/focus `#fabd2f`, and status colors mapped to canonical roles.
- Never use restricted `#665c54` for Visual Studio environment or editor text.
- Use the Visual Studio 2022+ theme structure and stable category GUIDs.
- Do not fabricate a VSIX identity or claim a VSIX build. The supported deliverable is `themes/Apollo.vstheme`, imported through Microsoft's Color Theme Designer, until a real extension identity and Windows VS SDK project are available.
