<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/banner-dark.svg">
    <img src="docs/assets/banner-light.svg" width="100%" alt="IFC Skills: teach any coding agent to query, check and safely edit IFC models.">
  </picture>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2F6BFF" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/IfcOpenShell-0.8-2F6BFF" alt="IfcOpenShell 0.8">
</p>

Ask a coding agent about an `.ifc` file. The [`ifc` skill](skills/ifc/SKILL.md)
queries the actual file with [IfcOpenShell](https://ifcopenshell.org/), checks
the official IFC schema, and gives answers based on the model.

## Requirements

- A coding agent that can run shell commands.
- Python 3.10 or newer.
- IfcOpenShell 0.8:

  ```bash
  python -m pip install "ifcopenshell>=0.8.4,<0.9"
  ```

  Use `python3` on macOS and Linux.

## Install

### Claude Code plugin

```bash
claude plugin marketplace add nbharathik/ifc-skills
claude plugin install ifc-skills@ifc-skills
```

### Other agents

With Node.js installed:

```text
npx skills add nbharathik/ifc-skills
```

For an agent that supports skill folders, copy `skills/ifc` into the agent's
skills folder and add:

```text
For anything involving IFC files, read ifc/SKILL.md and follow it.
```

## Use it

Open a project that contains an `.ifc` file and ask:

- `Summarise model.ifc`
- `What is the net wall area?`
- `Which walls have no fire rating?`
- `Check this model against requirements.ids`
- `What does IfcCovering mean?`
- `Add fire rating F30 to the external walls`

To call it explicitly in Claude Code, use `/ifc-skills:ifc`.

The agent stores temporary scripts in `.ifc-skills/`, which is ignored by git.
For large models it uses a fast mode that reads the file once.

## What's inside

```
skills/ifc/
├── SKILL.md          loaded for every IFC question
├── editing.md        read only before a change
├── viewer.md         read only when the IFC Viewer is connected
└── scripts/ifcs.py   fast mode for large models, copied into your project when needed
```

`SKILL.md` covers querying, IFC schema terms, properties, quantities, model
health, validation, IDS checks, safe editing, and the IFC Viewer.

The agent works in a `.ifc-skills/` folder in your project, which git ignores.

## IFC Viewer in your editor

In VS Code or a compatible editor, install the [IFC Viewer extension](https://github.com/nbharathik/vscode-ifc-viewer),
open the model, and click **Connect to agent**. You can then select an element
and ask about it.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
