# Writing outcome ledger

The corpus starts narrow. Grow the system's knowledge from finished work without teaching
it that assistant-originated prose is automatically the author's natural voice.

## Two evidence classes

- The identity's `corpus.jsonl` contains only sanitized, human-authored anchor passages.
  It can establish formal voice calibration.
- The project outcome ledger records every final or published piece. It shows accepted
  choices, content-type coverage, and repeated shapes, but it does not establish personal
  authorship by itself.

An assistant-assisted publication is useful evidence that the author accepted an outcome
for one assignment. It is not independent proof that the author would naturally produce
its phrases or structure. Approval establishes an assignment preference, not authorship.

## Record an outcome

Store project outcomes by persona at:

```text
<blog-home>/_blog-skill/writing-outcomes/<persona-name>.jsonl
```

After the author declares a piece final or published, run:

```bash
python3 <blog-writer-skill>/record-writing-outcome.py \
  --ledger <blog-home>/_blog-skill/writing-outcomes/<persona-name>.jsonl \
  --work-id <stable-id> \
  --persona <persona-name> \
  --date <YYYY-MM-DD> \
  --locator <path-or-url> \
  --content-type "conference abstract" \
  --mode persuade \
  --register peer-professional \
  --language en \
  --visibility public \
  --origin assistant-assisted \
  --event published
```

Origins:

- `human-drafted` — the author supplied the substantive prose
- `human-rewritten` — an assistant draft existed, but the author substantially rewrote it
- `assistant-assisted` — the system drafted or materially shaped the final prose

These labels record contribution history; none automatically modifies the anchor corpus.
Only the personal-identity owner may later promote a sanitized passage, and only after the
author confirms it was human-drafted. In v1, `human-rewritten` and `assistant-assisted`
outcomes are permanently excluded from the anchor corpus. This is deliberately stricter
than trying to estimate how much assistant wording or structure survived.

The ledger stores metadata and a locator, not the prose. During planning, read the last
five entries for the selected persona that share the target rhetorical mode or content
type:

```bash
python3 <blog-writer-skill>/select-writing-outcomes.py \
  --ledger <blog-home>/_blog-skill/writing-outcomes/<persona-name>.jsonl \
  --mode persuade \
  --content-type "conference abstract" \
  --limit 5
```

Use the result to see which forms have been attempted and which recorded shapes repeat.
Read a returned local artifact only when it still exists and the current assignment may
access its visibility. Do not automatically fetch URLs, follow missing locators, or infer
wording from metadata. This is a bounded planning check, not voice calibration.

## Sparse bootstrap

An empty anchor corpus is valid. Use explicit identity guidance, the author's current
assignment evidence, and normal editorial checks. Report formal calibration unresolved.
Record the finished outcome with honest origin. Over time the ledger grows immediately;
the anchor corpus grows only when genuinely human-authored evidence becomes available.

This asymmetry is intentional. It makes the workflow useful from the first assignment
without creating a feedback loop in which the system learns its own prose.
