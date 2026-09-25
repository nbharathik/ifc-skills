# IFC Viewer bridge

Part of the `ifc` skill. Read this when `.ifc-skills/viewer/` exists in the
project, or when the user wants to see something in the viewer.

The user may be working in VS Code or an editor built on it (Cursor, Windsurf,
VSCodium and others) with the model open in the IFC Viewer extension. The viewer
is for their eyes; you still answer from the file. The two talk through files in
`.ifc-skills/viewer/` at the root of the folder open in the editor (walk up from
the current directory to find it). The folder exists only while the user has
clicked the plug icon (Connect to agent) in the viewer toolbar. Never create it.

**The protocol:**

- **Connected** means `state.json` has `"open": true` and a `heartbeatAt` (ISO
  8601, UTC) no older than 3 times `heartbeatSeconds` (default 10). The viewer
  swaps the file atomically, so retry a failed read after about 50 ms.
- **`state.json`** holds `models` (each with a `path` relative to that folder,
  and `active`), `selection` (0 or 1 entries with `model`, `globalId`,
  `ifcClass`, `name`) and `highlights`.
- **Send a command** by writing JSON to `inbox/<id>.json.tmp` and then
  `os.replace` it to `inbox/<id>.json`; the viewer reads only complete `.json`
  files. Fields: `protocol: 1`; `id` (letters, digits, `.`, `_`, `-`, unique,
  for example `hl-` plus a uuid); `createdAt` in epoch milliseconds (commands
  older than 60 s are refused); `op` (`open`, `reload`, `select`, `highlight`,
  `isolate`, `fit`, `clear`); `model` (path relative to the folder, forward
  slashes); `globalIds` (at most 50,000); `label` and `color` for highlights;
  `what` for clear (`highlight`, `isolate`, `selection` or `all`).
- **Read the answer** from `outbox/<id>.json`, polling every 100 to 200 ms for
  up to 60 s (`open` waits for the model to load). Delete it after reading. It
  has `ok`, `requested`, `applied`, `missing` and, on failure, `error`. If no
  answer comes, delete your inbox file.

**How to use it:**

- "This", "the selected wall": query the selection's GlobalId instead of asking
  the user for one.
- "Show me": after a query that returns elements, offer to highlight them with a
  short label. Report "highlighted `applied` of `requested`" and name the
  `missing` ids. Branch on `ok`, never on the error text; `ok` with some
  `missing` is a normal partial success. The same label replaces its group.
- Storeys, buildings, curtain walls and stairs expand to everything below
  them, so send the storey rather than tens of thousands of ids. Types, psets,
  zones and systems do not resolve: expand them to products first.
- After an edit, highlight the changed GlobalIds in the edited copy with the
  label "changed by agent"; the viewer opens it by itself. It reloads open
  models when their file changes and re-applies highlights by GlobalId.
- If the viewer is not connected, do not mention it unless the user wants to
  see something. Then say: "Open the model in the IFC Viewer in your editor and
  click the plug icon (Connect to agent) in the viewer toolbar." Never read
  numbers off the viewer.
