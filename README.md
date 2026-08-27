# Apollo Theme for Visual Studio

A native Visual Studio 2022+ dark theme generated from the canonical Apollo palette. `themes/Apollo.vstheme` includes environment chrome, editor syntax and diagnostics, Command Window, and Output Window categories.

Repository: <https://github.com/apollo-theme/visual-studio-apollo-theme>

## Install

1. Install [Visual Studio Color Theme Designer 2022](https://marketplace.visualstudio.com/items?itemName=idex.colorthemedesigner2022).
2. In Visual Studio 2022, create a temporary **VSTheme Project**.
3. Close the generated theme editor, replace that project's generated `.vstheme` file with `themes/Apollo.vstheme`, and reopen it from Solution Explorer.
4. Choose **Preview** for a temporary check or **Apply** to make Apollo available to the IDE.

The designer does not document a direct standalone-file import command. The temporary project is therefore required to load and apply this source `.vstheme` without fabricating a VSIX. Keep a backup/export of your previous environment settings if you want to restore custom colors exactly.

## Activate

After applying the theme, open **Tools > Options > Environment > General** and select **Apollo** in the color-theme list. Restart Visual Studio if a tool window still caches old colors.

## Uninstall or restore

Because this repository ships theme source rather than an installed extension, there is no Apollo entry in **Manage Extensions**. Select another color theme under **Tools > Options > Environment > General** to stop using Apollo, then delete the temporary VSTheme project if it is no longer needed.

## Visual verification

Open a C# solution and verify:

- Main editor canvas is `#141617`; plain code text is `#cfbc97`.
- Keywords and syntax errors are red; strings and saved changes are green.
- Types and methods use gold `#fabd2f`; properties/information use blue; constants use magenta; namespaces use cyan.
- Active focus/search/current-statement cues use gold; selection uses dark brown without reducing text readability.
- Solution Explorer, tool windows, tabs, menus, status bar, Command Window, and Output Window remain legible.
- Normal interface/editor text never uses restricted `#665c54`.

## Develop and validate

Portable checks:

```sh
python3 scripts/generate.py --check
python3 scripts/check.py
python3 -m unittest discover -s tests -v
xmllint --noout --schema schemas/vstheme.xsd themes/Apollo.vstheme
```

One focused test:

```sh
python3 -m unittest tests.test_theme.VisualStudioThemeTests.test_editor_status_colors_match_palette
```

On Windows, run the native .NET XML validation path:

```powershell
pwsh -File scripts/validate.ps1
```

Both portable and Windows paths run in CI. `themes/Apollo.vstheme` is deterministic generated output; change mappings in `scripts/generate.py` and regenerate. `palette/apollo.json` must remain byte-for-byte canonical.

## VSIX limitation

This repository deliberately does **not** produce a VSIX. A correct Visual Studio theme VSIX needs a genuine extension/product identity, VSIX manifest, and Visual Studio SDK/MSBuild packaging project validated on Windows. No such identity or project was supplied, and inventing them would produce a misleading or unverified package. The native `.vstheme` is complete and loadable as source through a Color Theme Designer VSTheme project; Windows CI validates and stages it as the supported build artifact.

## License

MIT. Copyright (c) 2026 D0n9X1n.
