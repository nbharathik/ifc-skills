# Editing IFC models

Part of the `ifc` skill. Read this whole file before the first write to any
model, and follow it.

An IFC is a graph with references in both directions. A careless write produces
a file that opens cleanly in every viewer and is quietly wrong: the wrong
quantity in a tender, or a fire rating on the wrong side of a type and
occurrence split.

**The gate.** Edit only when the user asks for a change in this conversation.
"How many walls lack a fire rating?" is a question; "add F30 to them" is a
request. When unsure, treat it as a question.

**The procedure:**

1. **Copy first.** Work on `model.edited.ifc`; the original stays untouched
   until the user approves.
2. **Read, then propose.** Write one script with an `APPLY` switch. With
   `APPLY = False` it changes nothing and reports how many elements will
   change, how many already hold the value, and before and after for a sample.
   Show that, then wait.
3. **Apply** with `APPLY = True`, through `ifcopenshell.api`, never raw
   `create_entity`. The API keeps owner history, inverse relationships and
   GlobalIds consistent.
4. **Save atomically**: write to a temp `.ifc` in the same folder, then
   `os.replace` it onto the target. A viewer that reloads on change must never
   see half a file.
5. **Verify** against the written file: run again with `APPLY = False`, which
   must report nothing to change, then run schema validation.
6. **Report a diff**, not "done": count, attributes, before and after for a
   sample, and confirmation that the original is untouched.

**Good practice:**

- Make it re-runnable: sort targets by GlobalId, and skip elements that already
  hold the value.
- Check where a value lives first. `element_util.get_pset(el, pset,
  should_inherit=False)` shows the occurrence's own set. If the value comes from
  the type, propose editing the type (it affects all its occurrences) rather
  than silently overriding occurrences.
- Look for an existing set, material, classification or type by name before
  creating one. Adding a set that already exists creates a duplicate.
- Put values the user did not state (derived or estimated) in a clearly named
  set such as `Pset_AgentAuthored`, with source, method and date.
- Write values in the declared units (divide SI values by the unit scale).
- Confirm names with a lookup before writing them to a thousand elements.

**The API.** Its modules mirror IFC's domains, and you call
`ifcopenshell.api.<module>.<action>(model, ...)`:

- `pset`: `add_pset`, `edit_pset`, `add_qto`, `edit_qto`, `remove_pset`
- `attribute.edit_attributes`
- `root`: `create_entity`, `remove_product`, `copy_class`
- `spatial.assign_container`, `aggregate.assign_object`, `type.assign_type`
- `material`: `add_material`, `assign_material`
- `classification`: `add_classification`, `add_reference`
- `geometry`: `edit_object_placement`, `assign_representation`
- also `project`, `context`, `unit`, `group`, `system`, `document`, `sequence`,
  `cost`, `georeference`, `structural`, `alignment`, `drawing`, `style`

Check signatures before use; they change between releases.

**Things that look fine and are not:**

- A new element needs a placement and a container, or no viewer shows it:
  create, place, contain.
- In IFC2X3 one property set can serve many elements, so editing it changes all
  of them.
- Removing a storey or an aggregate parent orphans its children. Confirm every
  deletion and name what it orphans.
- Let the API create GlobalIds; never copy one, and never change an existing
  one.
- Never edit IFC text with a text editor, `sed` or string replacement.

If an apply run fails halfway, start again from the copy on disk. In fast mode,
run `ifcs.py open` on the copy again first.
