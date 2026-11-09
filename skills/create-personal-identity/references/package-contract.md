# Personal Identity Package Contract

Use this contract when creating, migrating, updating, or auditing a v1 personal identity.

## Manifest

Write `identity.json` with this minimum shape, replacing `example-author`:

```json
{
  "schema_version": 1,
  "type": "personal",
  "name": "example-author",
  "status": "draft",
  "entrypoint": "identity.md",
  "sources": "sources.md"
}
```

- `name` is lowercase kebab-case.
- `status` is `draft` or `approved`.
- `entrypoint` is exactly `identity.md`.
- `sources` is exactly `sources.md`.
- A missing `resources` field means an empty ordered list.

When evidence supports additional files, add `resources` as an ordered array:

```json
{
  "resources": [
    {"role": "voice", "path": "voice.md"},
    {"role": "composition", "path": "composition.md"},
    {"role": "examples", "path": "examples.md"},
    {"role": "corpus", "path": "corpus.jsonl"},
    {"role": "bio", "path": "bio.md"}
  ]
}
```

Each resource is an object with a lowercase kebab-case `role` and a non-empty `path`.
Paths do not start with `~`, are relative, and stay inside the package. Preserve resource
order because readers load them in that order.

## Content and provenance

- Put concise shared guidance and resource routing in `identity.md`.
- Add `voice`, `composition`, `examples`, `corpus`, or `bio` resources only when evidence supports
  them.
- In `sources.md`, record every source's location, date, scope, and authority.
- Trace each consequential inference to evidence.
- Label guidance Required, Preferred, Observed, Avoid, or Unresolved.
- Distinguish explicit preferences from observed patterns.
- Keep conflicting evidence and guidance visible.

## Optional corpus

Add a `corpus` resource only for sanitized, self-contained, human-authored passages. Read
and follow `skills/blog-writer/references/corpus-calibration.md`. Do not add assistant
drafts because the author approved or lightly edited them. Do not add reference authors,
uncertain corporate edits, coauthored prose, or translations in schema v1.

An empty corpus may explicitly record that a new identity has no qualifying prose yet.
Keep the evidence gap in `sources.md`; the writer then uses explicit identity guidance and
assignment evidence without claiming formal calibration.
