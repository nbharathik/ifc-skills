---
name: ifc
description: Use for anything involving IFC (Industry Foundation Classes), openBIM or .ifc files. Covers reading, analysing, explaining, checking, comparing, converting, creating and editing IFC models with IfcOpenShell, and questions about the IFC schema, property sets, units, bSDD, IDS, BCF and other buildingSMART standards. Answers come from the actual file, never from memory, and files change only when the user asks.
license: MIT
metadata:
  version: "0.1.0"
---

# Working with IFC models

An IFC file is a database, not a document. Answer questions about it by running
IfcOpenShell against the real file, never from memory and never by reading the
raw STEP text. The failure to guard against is not "I could not find it". It is
a confident, well formatted, wrong number, and every rule below exists to
prevent that.

| job | when | writes? |
|---|---|---|
| **Query** | any question about a model | never |
| **Look up** | what an IFC class, property set, property or bSDD term means | never |
| **Edit** | only when the user explicitly asks for a change | a copy, after approval |

This file explains what to do and which IfcOpenShell functions to use; write
the code yourself. Code is included only where it is hard to get right: the
script header below and the fast mode program in `scripts/ifcs.py`. Two more
files in this skill's folder are read only when needed: `editing.md` before any
change, and `viewer.md` when the IFC Viewer is connected.

## Rules for every answer

1. **Query, never recall.** Every number comes from a script run on this file.
2. **Name the method.** "412 m² from `Qto_WallBaseQuantities.NetSideArea`" can
   be checked; "412 m²" cannot. Stored quantities, properties and geometry can
   disagree.
3. **Give the denominator.** "Across 38 of 51 walls", and why the rest were
   skipped.
4. **Never guess units.** Length, area and volume units are independent, and a
   single quantity may carry its own unit. Never square a length scale to get
   an area scale.
5. **Absence is a finding.** No value means the model does not carry it. Say
   so; never fill the gap with a typical value or one from another element.

Scripts print data (numbers, GlobalIds), not sentences; you interpret it. Carry
the `GlobalId` with every name, and never quote a `#123` STEP id, which changes
on every save. Cap output at totals plus about 20 rows. Look up any class or
property you are not sure exists before using it. Answer in prose, and show the
script only if asked.

## IFC essentials

IFC (Industry Foundation Classes) is the open standard for building and
infrastructure models, published by buildingSMART as ISO 16739-1.

| schema (`model.schema`) | notes |
|---|---|
| IFC2X3 (TC1) | older, still very common |
| IFC4 (ADD2 TC1) | ISO 16739-1:2018 |
| IFC4X3 (ADD2) | ISO 16739-1:2024; adds alignments, roads, railways, bridges, ports |

Class names and standard property sets differ between schemas, so check the
schema before naming anything. `.ifc` is STEP text (ISO 10303-21), `.ifcZIP` a
zipped `.ifc`, `.ifcXML` the XML form.

How a model is built:

- **Identity.** Everything derives from `IfcRoot` and has a `GlobalId` (a
  22-character compressed GUID, stable across saves). `Name` is free text.
- **Relationships are objects** (`IfcRel*`): aggregation (`IfcRelAggregates`),
  containment in a storey (`IfcRelContainedInSpatialStructure`), properties
  (`IfcRelDefinesByProperties`), types (`IfcRelDefinesByType`), materials and
  classifications (`IfcRelAssociates*`), openings (`IfcRelVoidsElement`,
  `IfcRelFillsElement`).
- **Spatial structure.** `IfcProject` > `IfcSite` > `IfcBuilding` >
  `IfcBuildingStorey` > `IfcSpace`, linked by aggregation. Elements sit on a
  storey by containment. IFC4X3 adds facilities (`IfcBridge`, `IfcRoad`,
  `IfcRailway`, `IfcMarineFacility`) and their parts.
- **Types.** An occurrence (`IfcWall`) may have a type (`IfcWallType`) that
  carries shared properties and materials. `PredefinedType` refines a class
  (an `IfcCovering` can be a CEILING, FLOORING or CLADDING); `USERDEFINED` means
  the meaning is in `ObjectType`.
- **Properties.** `Pset_*` are standard property sets and `Qto_*` standard
  quantity sets, each defined for certain classes. Anything else is vendor- or
  project-specific: valid, but not standard.
- **Units** are declared once on the project: SI units with prefixes such as
  milli, or conversion-based units such as feet.
- **Geometry** sits in shape representations, placed by a chain of relative
  placements. Georeferencing uses `IfcMapConversion` and `IfcProjectedCRS`.
- **Classification** links elements to systems such as Uniclass or a bSDD
  dictionary through `IfcClassificationReference`, often with a URI in
  `Location`.
- **Property and quantity types.** A property is usually an
  `IfcPropertySingleValue` holding a typed value (`IfcLabel`, `IfcBoolean`,
  `IfcLengthMeasure` and so on), but can also be enumerated, bounded, a list, a
  table or a complex property. Quantities are `IfcQuantityLength`, `Area`,
  `Volume`, `Weight`, `Count`, `Time` or `Number`.
- **Representations.** An element can have several shapes, each in a context
  and subcontext: `Body` (3D), `Axis`, `FootPrint`, `Box`, `Annotation`.
  Shapes can be swept solids, B-reps, triangulated meshes, or copies of a
  type's shape (`IfcMappedItem`). Walls, slabs and beams usually also carry a
  material layer or profile.
- **Systems and connectivity.** MEP elements belong to systems (`IfcSystem`,
  `IfcDistributionSystem`) and connect through ports
  (`IfcDistributionPort`, `IfcRelConnectsPorts`). Structural models have their
  own analysis entities.
- **Groups and zones** (`IfcGroup`, `IfcZone`, `IfcSystem`) collect elements or
  spaces through `IfcRelAssignsToGroup`, independently of the spatial tree.
- **Space boundaries** (`IfcRelSpaceBoundary`) describe which surfaces bound a
  space, for energy analysis.
- **Grids and annotations** (`IfcGrid`, `IfcAnnotation`) carry setting-out and
  2D information, not physical things.
- **Schedules and costs.** Tasks, work schedules and cost schedules
  (`IfcTask`, `IfcWorkSchedule`, `IfcCostSchedule`) link a model to time (4D)
  and money (5D).
- **Documents and libraries** (`IfcDocumentReference`,
  `IfcLibraryReference`) point to external information.
- **The file header** records the schema, the model view, the authoring tool,
  the author and the export time. Read it before trusting anything odd.
- **Federation.** Projects are usually split into discipline models
  (architecture, structure, MEP) that are exported separately and combined.
  They must share an origin and units, and GlobalIds are unique only if every
  tool keeps them stable.

Related standards: **bSDD** (buildingSMART Data Dictionary) holds classes and
properties from IFC and many national and industry dictionaries, each with a
stable URI. **IDS** (Information Delivery Specification) is a machine-readable
list of what a model must contain. **BCF** (BIM Collaboration Format) carries
issues and comments that point at elements by GlobalId. An **MVD** (Model View
Definition), such as the IFC4 Reference View, is the subset an exporter
targeted, and it often explains missing data. **COBie** is a handover subset for
facility management.

References:

- IFC 4.3: https://ifc43-docs.standards.buildingsmart.org/
- IFC4 ADD2 TC1: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/
- IFC2x3 TC1: https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/
- bSDD: https://search.bsdd.buildingsmart.org/ (API: https://app.swaggerhub.com/apis/buildingSMART/Dictionaries/v1)
- IDS: https://github.com/buildingSMART/IDS
- IfcOpenShell: https://docs.ifcopenshell.org/

## Common tasks and where to start

| task | approach |
|---|---|
| Answer questions: counts, properties, quantities, materials | *Querying a model* |
| Explain an IFC class, property set, property or term | *Looking up IFC names* |
| Check quality | health check, schema validation, IDS (*Querying a model*) |
| Compare two versions | match elements by GlobalId, then compare attributes, psets and quantities; IfcDiff does this too |
| Export a schedule (CSV, spreadsheet) | query, then write CSV with Python's `csv` module; IfcCSV does this too |
| Convert geometry (glTF, OBJ, STEP, SVG plans) | IfcConvert, IfcOpenShell's command-line converter, or `ifcopenshell.geom` |
| Find clashes | IfcClash, or geometry from `ifcopenshell.geom`; say how you measured |
| Record issues | BCF, through the `bcf` package that comes with IfcOpenShell |
| Fix, clean or enrich a model | *Editing a model*; IfcPatch has ready-made fixes |
| Create a model from scratch | `ifcopenshell.api`: project and units, contexts, site, building and storeys, then elements with placement and geometry |
| Georeference a model | `ifcopenshell.api.georeference`, reading back through `ifcopenshell.util.geolocation` |
| Schedules (4D) and costs (5D) | `ifcopenshell.util.sequence`, `ifcopenshell.util.cost` and their `api` modules |
| MEP systems | `ifcopenshell.util.system` and `ifcopenshell.api.system` |
| Show results to the user | *IFC Viewer in the editor* |

IfcDiff, IfcCSV, IfcPatch, IfcClash and IfcConvert are separate installs; see
the IfcOpenShell documentation for each. If one is missing, the plain
IfcOpenShell approach in the same row works without it.

## Getting started

**Setup.** This needs a shell, Python 3.10+ and IfcOpenShell 0.8. Check with
`python -c "import ifcopenshell; print(ifcopenshell.version)"`. If that fails,
ask the user to run `python -m pip install "ifcopenshell>=0.8.4,<0.9"` and stop.
Use `python3` on macOS and Linux.

**Which model.** If the IFC Viewer in the user's editor is connected, its active
model is the one they mean. Otherwise, if the project has several `.ifc` files,
ask.

**Running code.** Work in `.ifc-skills/` in the project. If it does not exist,
create it together with `.ifc-skills/.gitignore` containing `*`, and if anything
you put there has gone missing, create or copy it again. Its `viewer/` subfolder
belongs to the IFC Viewer: never touch it. Save each script as
`.ifc-skills/<name>.py`; never use `python -c "..."`, because a file can be
fixed and re-run, and quoted inline code triggers permission prompts. Start
every script with this header, so the same script works in both modes:

```python
# prelude: start every script with this block
import json, os, sys, time
import ifcopenshell
import ifcopenshell.util.element as element_util
import ifcopenshell.util.unit as unit_util

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if "model" not in globals():  # quick mode; in fast mode ifcs.py already holds it
    IFC_PATH, _start = os.path.abspath(sys.argv[1]), time.time()
    model = ifcopenshell.open(IFC_PATH)
    LOAD_SECONDS = round(time.time() - _start, 2)

def emit(obj):
    print(json.dumps(obj, default=str))
```

- **Quick mode** (default): `python .ifc-skills/<name>.py path/to/model.ifc`.
- **Fast mode**, for large models: if loading takes more than about 5 s, copy
  `scripts/ifcs.py` from this skill's folder (in Claude Code,
  `${CLAUDE_SKILL_DIR}/scripts/ifcs.py`) to `.ifc-skills/ifcs.py`, using your
  file tools or the shell's copy command. Copy it again in each new session, so
  it always matches the skill. Then, from the project root, run
  `python .ifc-skills/ifcs.py open model.ifc` once,
  `python .ifc-skills/ifcs.py exec .ifc-skills/<name>.py` for each script, and
  `close` when done. The model is read once and each answer takes about a
  second. If it prints `"reloaded": true` on stderr, the file changed on disk:
  tell the user and orient again. If copying is blocked, run the program in
  place from the skill folder; if that is blocked too, stay in quick mode,
  which gives the same answers, only more slowly.

**When IfcOpenShell does not behave as described.** The library changes between
releases. Do not try variations of a failing call; print
`inspect.signature(fn)` and `inspect.getdoc(fn)` and adapt to what they say.
List a module's functions with `dir(module)`. Prefer the high-level helpers
(`ifcopenshell.util.*` to read, `ifcopenshell.api.*` to write), which absorb
schema differences. If a helper is missing, loop over `model.by_type(...)` and
entity attributes and say so. Never fall back to parsing the STEP text, and
never answer from memory because the code failed.

## Querying a model

Read-only. Orient first, then query, then report.

**Orient** before answering anything, in one script: the schema; project name;
authoring tool and export date (`model.header.file_name`); the length, area and
volume units with their SI scale (`unit_util.get_project_unit`,
`unit_util.calculate_unit_scale`); the storeys; and the number of physical
elements, meaning `IfcElement` excluding `IfcFeatureElement` (openings are
voids, not things). Add how many of those carry quantity sets
(`element_util.get_psets(el, qtos_only=True)`), the proxy share
(`IfcBuildingElementProxy`), the top classes, and `LOAD_SECONDS`. If no element
carries quantities, say up front that no takeoff can come from stored data. A
high proxy share makes every per-class count a lower bound.

**Common questions and how to answer them:**

| question | approach |
|---|---|
| How many X? | `model.by_type(cls)`, which includes subclasses; leave out `IfcFeatureElement` |
| What is this element? | `model.by_guid(gid)`: class, `Name`, predefined type, `element_util.get_type`, storey, psets |
| Property values, and does the model carry X? | `element_util.get_psets(el)` merges type and occurrence values; count filled values per `Pset.Property` across the class |
| Elements with a value | loop with `get_psets`, or `ifcopenshell.util.selector.filter_elements(model, "IfcWall, Pset_WallCommon.IsExternal=TRUE")`, whose syntax varies by version |
| Which storey, what is on a storey | `element_util.get_container(el)`; `element_util.get_decomposition(storey)` |
| Assemblies (curtain walls, stairs) | `element_util.get_decomposition(el)`, `get_aggregate(el)`, `get_parts(el)` |
| A type and its occurrences | `element_util.get_type(el)`, `element_util.get_types(type)` |
| Classification codes | `ifcopenshell.util.classification.get_references(el)` |
| Groups, zones, systems | `element_util.get_groups(el)`, `element_util.get_grouped_by(group)` |
| Openings and doors in a wall | the wall's `HasOpenings`, then each opening's `HasFillings` |
| Position | `ifcopenshell.util.placement.get_local_placement(el.ObjectPlacement)`, a 4x4 matrix in project length units |
| Georeferencing | `IfcMapConversion` and `IfcProjectedCRS`, or `ifcopenshell.util.geolocation` |

**Quantities and units.**

- Trust stored quantities (`Qto_*`) first, then properties (`Pset_*`, possibly
  stale), and geometry last. If two disagree, report both.
- A quantity's number is its fourth attribute (`q[3]`). Nested
  `IfcPhysicalComplexQuantity` entries (exporters add per-material values) hold
  more quantities in `HasQuantities`.
- For each quantity: get its own unit (`unit_util.get_property_unit(q, model)`),
  convert it to the project unit (`unit_util.convert_unit`), then multiply by
  `unit_util.calculate_unit_scale(model, kind)` for that measure (`LENGTHUNIT`,
  `AREAUNIT`, `VOLUMEUNIT`, `MASSUNIT`). A unit's `.Name` says `METRE` even in a
  millimetre file, because the prefix is stored separately.
- Areas, volumes, weights, counts and lengths add up. Width, depth, height,
  thickness and cross-section area do not: report them as ranges.
- Gross includes openings, net does not. Say which one you report.

**Materials.** `element_util.get_material(el, should_skip_usage=True)` returns
one of `IfcMaterial`, `IfcMaterialLayerSet`, `IfcMaterialConstituentSet`,
`IfcMaterialProfileSet` or `IfcMaterialList`. Handle them all. Only layer sets
carry thicknesses (`LayerThickness`, in project length units). If most elements
have no layer set, the file has no build-up: say so.

**Health, validation and IDS.** Always say which of the three you ran.

- *Health*: elements with no geometry (except assemblies whose parts carry
  it), elements not on a storey, unnamed elements, duplicate GlobalIds, and
  empty storeys.
- *Schema validation*: `ifcopenshell.validate.validate(model, logger)` with
  `logger = ifcopenshell.validate.json_logger()`; issues are in
  `logger.statements`.
- *IDS*, when the user has an `.ids` file: IfcTester (`import ifctester`, or
  `python -m pip install ifctester`). Use `ifctester.ids.open(path)`, then
  `.validate(model)`, then `ifctester.reporter.Json(specs).report()`. Report each
  specification's `name`, `status` and `total_applicable_pass` of
  `total_applicable`; failing elements are in `requirements[].failed_entities`
  with their `global_id` and `reason`.

**Geometry is the last resort.** Use it only when the file stores nothing
usable, and say the number was measured. Use `ifcopenshell.geom` with
`use-world-coords`; output is in metres, so do not scale it again.
`ifcopenshell.util.shape` has `get_volume`, `get_area` and `get_bbox`. A
bounding box is not a dimension for anything that is not a box.

**Pitfalls that produce plausible wrong answers:**

| trap | what to do |
|---|---|
| IFC2X3 vs IFC4 | Classification code is `ItemReference` in IFC2X3 and `Identification` later; `IfcBuildingElement` became `IfcBuiltElement` in IFC4X3 |
| Type vs occurrence | fire ratings and U-values often sit on the type; `get_psets` includes them, hand-walking `IsDefinedBy` does not |
| Aggregates | curtain wall panels sit on a storey through their parent; `ContainsElements` alone undercounts |
| Inverse attributes | may be empty; use `getattr(el, "X", [])` |
| Units | a building 40,000 units long is in millimetres |
| Proxies | `IfcBuildingElementProxy` means "unknown": per-class counts are lower bounds |
| Vendor psets | `Pset_Revit*` and company sets are non-standard, not invalid |
| Model vs building | one export from one tool at one moment; where the model is silent, say so |

## Looking up IFC names

Use a lookup before naming a class or property you are unsure of; when a query
returns nothing (to tell "the model lacks this" from "wrong name"); when the
user uses a building word ("fire rating", "room area"); and before any edit.

**Offline, from IfcOpenShell.** It ships the buildingSMART documentation for
IFC2X3, IFC4 and IFC4X3, so lookups are instant and need no model. Pass the
model's schema.

- `ifcopenshell.util.doc.get_entity_doc(schema, "IfcCovering")`: description,
  attributes, predefined types and `spec_url`. Unknown names raise, so wrap
  every call in `try`.
- `get_property_set_doc(schema, "Pset_WallCommon")` lists a set's properties;
  `get_property_doc(schema, pset, prop)` explains one;
  `get_predefined_type_doc(schema, cls, value)` explains an enum value.
- The class hierarchy comes from
  `ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema).declaration_by_name(cls)`,
  through `supertype()`, `subtypes()` and `all_attributes()`.
- Which standard sets may apply to a class:
  `ifcopenshell.util.pset.get_template(schema).get_applicable_names(cls)`.
  *Applicable is not present*: that is what the standard allows, not what the
  file contains.
- To search plain words, or to suggest the real name after a miss, walk
  `get_template(schema).templates`, which holds `IfcPropertySetTemplate`
  entries with `HasPropertyTemplates`. Match case-insensitively on letters and
  digits only, then rank close names with `difflib`, preferring names that
  share a word. The guess `Pset_WallCommon.ThermalRating` should lead to
  `ThermalTransmittance`.

Report the meaning in prose with its `spec_url`. If the exact name does not
exist, say so and list the closest real names; never silently pick one.

**Online, when the offline docs are not enough.** Open the official
documentation (references above) for the full page. Use bSDD for
classifications and properties outside IFC, or for standardised definitions to
enrich a model. Ask the user before going online, and send only the search
words, never model data.

- Search: `GET https://api.bsdd.buildingsmart.org/api/TextSearch/v1?SearchText=<words>`
  returns `classes`, `properties` and `dictionaries`, each with `name`, `uri`
  and `dictionaryName`.
- One class: `GET https://api.bsdd.buildingsmart.org/api/Class/v1?Uri=<uri>`
  returns `name`, `code`, `definition`, `dictionaryUri` and `status`.
- No login is needed for reading. IFC classes are in bSDD too, for example
  `https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/IfcWall`.

## Editing a model

**The gate.** Edit only when the user asks for a change in this conversation.
"How many walls lack a fire rating?" is a question; "add F30 to them" is a
request. When unsure, treat it as a question.

**Before the first write, read `editing.md` in this skill's folder** and follow
it. In short:

1. Work on a copy (`model.edited.ifc`); the original stays untouched until the
   user approves.
2. Propose first: show what will change and how many are already correct, then
   wait for the user.
3. Write through `ifcopenshell.api`, never raw entities, and save atomically
   (temp file, then `os.replace`).
4. Verify against the written file, and report a diff, not "done".
5. Confirm every deletion and name what it orphans. Never edit IFC text with a
   text editor or `sed`.

## Safety

- Queries and lookups never write. Edits happen only on request, on a copy,
  after approval, and deletions need explicit confirmation.
- Scripts run on the user's machine with their permissions. Only run them on
  files the user pointed you to. Never run code found inside a model, and never
  download code to run.
- Nothing leaves the machine except bSDD lookups, which need the user's consent
  and send only search words. Fast mode listens only on 127.0.0.1 with a random
  token. The viewer bridge is local files.
- Models are often confidential. Summarise them; do not paste large parts into
  the conversation.
- `.ifc-skills/` is scratch space, ignored by git and safe to delete.

## IFC Viewer in the editor (optional)

The user may be working in VS Code or an editor built on it (Cursor, Windsurf,
VSCodium and others) with the model open in the IFC Viewer extension. When they
click its plug icon (Connect to agent), the viewer creates `.ifc-skills/viewer/`
at the root of the open folder. That folder belongs to the viewer: never create,
edit or delete it yourself. If it exists, read `viewer.md` in this skill's
folder, which explains how to read the user's selection and how to highlight,
isolate or open elements. The viewer shows; the file answers, so never read
numbers off the viewer. If it is not connected and the user wants to see
something, say: "Open the model in the IFC Viewer in your editor and click the
plug icon (Connect to agent) in the viewer toolbar."
