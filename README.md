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

Ask a coding agent about an `.ifc` file and it usually reads the raw text and
drowns, or answers from general BIM knowledge and invents a number that looks
real. The [`ifc` skill](skills/ifc/SKILL.md) makes it work the way an expert
would: query the actual file with [IfcOpenShell](https://ifcopenshell.org/),
look terms up in the official schema, and answer honestly.

## Requirements

- A coding agent that can run shell commands.
- Python 3.10 or newer with IfcOpenShell 0.8:

  ```bash
  python -m pip install "ifcopenshell>=0.8.4,<0.9"
  ```

  Use `python3` on macOS and Linux. For IDS checks the agent also uses
  IfcTester (`python -m pip install ifctester`).

Always install the whole `skills/ifc` folder, not only `SKILL.md`.

## Install

### Claude Code

**As a plugin** (recommended). In a terminal:

```bash
claude plugin marketplace add nbharathik/ifc-skills
claude plugin install ifc-skills@ifc-skills
```

Inside a Claude Code session in the terminal, use the same commands with
`/plugin` instead of `claude plugin`. The VS Code chat panel cannot run
`/plugin`, so install from a terminal and then start a new chat.

**As a skill folder.** Copy `skills/ifc` to `~/.claude/skills/ifc/` for all
projects, or to `.claude/skills/ifc/` inside one project.

### Codex

Copy `skills/ifc` to `~/.agents/skills/ifc/` for all projects, or to
`.agents/skills/ifc/` inside one project. You can also install it from Codex with
the skill installer and this folder URL:

```text
$skill-installer https://github.com/nbharathik/ifc-skills/tree/main/skills/ifc
```

### Cursor, GitHub Copilot, Gemini CLI, Windsurf and others

With Node.js installed, one command installs the skill for the agents you use:

```bash
npx skills add nbharathik/ifc-skills        # this project
npx skills add nbharathik/ifc-skills -g     # all projects
```

Add `-a <agent>` to choose agents; `npx skills --help` lists them. Without
Node.js, copy `skills/ifc` to `~/.agents/skills/ifc/`, which Cursor, GitHub
Copilot and Gemini CLI read.

### Any other agent

Copy `skills/ifc` into your project and add this line to the agent's
instructions (`AGENTS.md`, a rules file or the system prompt):

```text
For anything involving IFC files, read ifc/SKILL.md and follow it.
```

## Use it

Open a project that contains an `.ifc` file and ask. The skill loads by itself
whenever a question involves IFC:

| you want to | ask for example |
|---|---|
| understand a model | *"Summarise model.ifc"* |
| get numbers | *"What is the net wall area?"*, *"How many doors per storey?"* |
| check properties | *"Which walls have no fire rating?"* |
| check quality | *"Is this model healthy?"*, *"Check it against requirements.ids"* |
| learn IFC terms | *"What does IfcCovering mean?"*, *"Which pset holds U-values?"* |
| change the model | *"Add fire rating F30 to the external walls"* (works on a copy and waits for your approval) |

To call it explicitly, use `/ifc-skills:ifc` for the Claude Code plugin, `/ifc`
for a Claude Code skill folder, or `$ifc` in Codex.

The agent keeps its scripts in a `.ifc-skills/` folder in your project. It
ignores itself in git and is safe to delete. For large models the agent switches
to a fast mode that reads the file once.

## Update and remove

| installed with | update | remove |
|---|---|---|
| Claude Code plugin | `claude plugin marketplace update ifc-skills`, then `claude plugin update ifc-skills` | `claude plugin uninstall ifc-skills` |
| `npx skills` | run the same `npx skills add` command again | see `npx skills --help` |
| a copied folder | copy the new `skills/ifc` over it | delete the `ifc` folder |

## What's inside

```
skills/ifc/
├── SKILL.md          loaded for every IFC question
├── editing.md        read only before a change
├── viewer.md         read only when the IFC Viewer is connected
└── scripts/ifcs.py   fast mode for large models, copied into your project when needed
```

`SKILL.md` covers:

| section | what the agent learns |
|---|---|
| Rules | query, never recall; name the method; give the denominator; never guess units; treat missing data as a finding |
| IFC essentials | versions, file formats, how a model is built, related standards (bSDD, IDS, BCF, MVD), official links |
| Common tasks | where to start for querying, checking, comparing, exporting, converting, creating and editing |
| Getting started | setup, running scripts, a fast mode for large models, what to do when IfcOpenShell changes |
| Querying | orientation, common questions, quantities and units, materials, health, validation, IDS, pitfalls |
| Looking up | the schema docs shipped with IfcOpenShell, and bSDD online |
| Editing | only when asked, and always on a copy with your approval (details in `editing.md`) |
| Safety | what runs where, and what never leaves your machine |
| IFC Viewer in the editor | show results in the viewer extension (details in `viewer.md`) |

The agent works in a `.ifc-skills/` folder in your project, which git ignores.

## IFC Viewer in your editor

Working in VS Code or an editor built on it, such as Cursor, Windsurf or
VSCodium? Install the [IFC Viewer extension](https://github.com/nbharathik/vscode-ifc-viewer),
open the model, and click the plug icon (**Connect to agent**). You can then
click an element and ask about it, or ask the agent to highlight what it found.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
