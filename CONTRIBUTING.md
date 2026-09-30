# Contributing

Thanks for contributing.

The whole project is one skill, in [`skills/ifc/`](skills/ifc/SKILL.md):

| file | loaded |
|---|---|
| `SKILL.md` | for every IFC question; keep it under about 500 lines |
| `editing.md` | only before a change |
| `viewer.md` | only when the IFC Viewer is connected |
| `scripts/ifcs.py` | copied into the user's project for fast mode |

Put material in `SKILL.md` only if most conversations need it; otherwise it
belongs in a file that `SKILL.md` points to.

## Rules for the skill

- Explain what to do and name the IfcOpenShell functions; agents write routine
  code themselves. Add code only where it is hard to get right. Today that is the
  script header (`# prelude` in `SKILL.md`) and `scripts/ifcs.py`.
- The safety rules for editing stay in `SKILL.md` too, so they apply even if the
  agent never opens `editing.md`.
- Prefer general IFC knowledge that stays true across IfcOpenShell releases.
- Every rule must keep answers honest: say where a number came from and out of
  how many.
- Check that every function you name exists in the current IfcOpenShell.
- Bump `metadata.version` in the file's header when you change it.

## Try it in dev mode

Run Claude Code from a folder that holds an `.ifc` file (for example `dev/`),
pointing at this repository:

```
claude --plugin-dir "C:\path\to\ifc-kit"
```

Inside the session:

- `/reload-plugins` picks up edits to the skill without restarting.
- `/help` or `/skills` should list `ifc-skills:ifc`.
- Ask an IFC question, or call it directly with `/ifc-skills:ifc`.
- `claude plugin validate .` checks the manifests.

To keep it always on, install it from GitHub once published:

```
/plugin marketplace add nbharathik/ifc-skills
/plugin install ifc-skills@ifc-skills
```

Or from a local clone: `/plugin marketplace add C:\path\to\ifc-kit`.

## Check a change before opening a pull request

1. Load the skill in a test project next to an `.ifc` model, for example with
   `claude --plugin-dir <path to this repository>`.
2. If you changed code, run it: the prelude plus a small script in quick mode,
   and `scripts/ifcs.py` with `open`, `exec` and `close`, both copied into the
   project and run in place.
3. Ask an agent a few real questions and check that the answers name their
   method and denominator.

Never commit IFC models. They are ignored by git; keep private ones in `dev/`.

## Publishing a release

1. Set the same version in `skills/ifc/SKILL.md` (`metadata.version`) and
   `.claude-plugin/plugin.json`.
2. Run `claude plugin validate .`.
3. Push to GitHub. `npx skills add` and the Claude Code plugin marketplace both
   install straight from the repository, so there is nothing else to upload.
