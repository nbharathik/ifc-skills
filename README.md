<p align="center">
  <img src="docs/assets/ifc-skills-logo.png" width="112" alt="IFC Skills logo">
</p>

<h1 align="center">IFC Skills</h1>

<p align="center"><strong>One skill that teaches any coding agent to work with IFC and openBIM.</strong></p>

Ask a coding agent about an `.ifc` file and it usually reads the raw text and
drowns, or answers from general BIM knowledge and invents a number that looks
real. The [`ifc` skill](skills/ifc/SKILL.md) makes it work the way an expert
would: query the actual file with [IfcOpenShell](https://ifcopenshell.org/),
look terms up in the official schema, and answer honestly.

## How to use

First install IfcOpenShell: `python -m pip install "ifcopenshell>=0.8.4,<0.9"`.
Then pick one option. Always install the whole `skills/ifc` folder, not only
`SKILL.md`.

**1. Copy the folder (any agent).** Copy `skills/ifc` into your project and tell
your agent to read `ifc/SKILL.md` for IFC work. That is all.

**2. Install it as a skill,** so the agent loads it by itself:

| agent | copy the `ifc` folder to |
|---|---|
| Claude Code, one project | `.claude/skills/ifc/` |
| Claude Code, all projects | `~/.claude/skills/ifc/` |
| Codex, Cursor, GitHub Copilot, Gemini CLI, one project | `.agents/skills/ifc/` |
| the same, all projects | `~/.agents/skills/ifc/` |

**3. One command for many agents** (Claude Code, Codex, Cursor, Copilot, Gemini
and more; needs Node.js):

```bash
npx skills add nbharathik/ifc-skills          # this project
npx skills add nbharathik/ifc-skills -g       # all projects
npx skills add nbharathik/ifc-skills -g -a claude-code codex   # chosen agents
```

**4. Claude Code plugin:**

```bash
claude plugin marketplace add nbharathik/ifc-skills
claude plugin install ifc-skills@ifc-skills
```

Inside a Claude Code session, the same commands start with `/plugin`.

Then ask: *"Summarise model.ifc"*, *"What is the net wall area?"*, *"Which
walls have no fire rating?"*, *"What does IfcCovering mean?"*

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
