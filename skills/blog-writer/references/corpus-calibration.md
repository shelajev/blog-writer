# Corpus-backed voice calibration

A personal identity may have a private corpus of sanitized, human-authored passages. Use
it to find evidence of durable voice across writing forms, not to reproduce the author's
most common structure.

## Corpus resource

A v1 personal identity may declare this optional resource:

```json
{"role": "corpus", "path": "corpus.jsonl"}
```

The package must remain private when the corpus contains non-public prose. Each non-empty
line is one JSON object:

```json
{
  "id": "stable-id",
  "text": "A sanitized, self-contained passage of roughly 100-400 words.",
  "source": "https://example.test/post#section",
  "date": "2026-05-14",
  "language": "en",
  "privacy": "public",
  "provenance": "human-authored",
  "rhetorical_mode": "persuade",
  "register": "peer-professional",
  "content_type": "conference abstract",
  "status": "active"
}
```

All fields are required. Allowed values are:

- `privacy`: `public` or `private`
- `provenance`: `human-authored`
- `rhetorical_mode`: `explain`, `persuade`, `propose`, `critique`, `narrate`, or
  `correspond`
- `register`: `casual`, `peer-professional`, or `executive-formal`
- `status`: `active` or `deprecated`

`date` accepts `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, or `unknown`. Do not invent precision to
make an older source sortable.

`content_type` is open vocabulary: conference abstract, blog post, LinkedIn post, email,
GitHub review comment, tutorial, strategy memo, and so on. It describes form but does not
drive similarity. Different forms are adjacent when they share rhetorical mode and
register. This is the system's deliberately limited form of fuzzy matching.

Do not ingest an assistant draft merely because the author approved or lightly edited it.
Do not ingest reference authors, corporate edits of uncertain origin, coauthored prose, or
translated prose in v1. Keep those in provenance records outside the retrievable corpus.
Later schema versions may add them only with explicit evidence and evaluation.

## Assignment classification

Record five properties before selection:

- content type, in the assignment's own words
- rhetorical mode
- register
- language
- visibility: `public` or `private`

Choose the rhetorical mode by the piece's main job, not its channel. A LinkedIn post may
explain, persuade, narrate, or propose. An email may correspond while also proposing; pick
the job that governs its argument and record the secondary job in working notes.

## Select passages

Run:

```bash
python3 <blog-writer-skill>/select-calibration.py \
  --corpus <identity-root>/corpus.jsonl \
  --content-type "conference abstract" \
  --mode persuade \
  --register peer-professional \
  --language en \
  --visibility public
```

The selector filters by provenance, active status, language, privacy compatibility,
rhetorical mode, and register. For a public assignment, it may select only `privacy:
public` passages. For a private assignment, it may select both public and private passages.
It first prefers `content_type` values different from the target assignment, then prefers
different types from one another. The model therefore sees durable behavior across forms
rather than three templates for the form being drafted. If insufficient cross-form
evidence exists, same-form passages remain eligible and the output reports that limitation.

Two or three matching passages make the corpus evidence `ready`. Fewer leave it
`unresolved`. With unresolved evidence, draft from the selected identity's explicit
guidance and the current assignment's author-preservation contract. Do not retrieve
reference-author or assistant prose, silently substitute another persona, or claim formal
voice calibration.

## Creativity contract

The passages answer: how does this author establish stakes, qualify claims, relate to the
reader, connect paragraphs, and move an argument in this rhetorical situation?

They do not prescribe an opening, outline, ending, length, phrase, joke, punctuation rate,
or device quota. Apply these rules:

- Compare functions and relationships, not surface templates.
- Name one meaningful difference the new assignment should retain from every selected
  passage set.
- Prefer passages from different content types.
- Keep assignment-backed departures even when the corpus lacks precedent.
- Evaluate voice fidelity and originality separately.
- Treat an author-written new form as identity expansion, not automatic drift.
- Never use corpus frequency as a requirement.

Run the structural-convergence audit independently. Corpus readiness does not establish
originality, and originality does not establish voice fidelity.

## Updating the corpus

Only the personal-identity owner may add records. Add the final human-authored passage,
not an earlier assistant draft. If authorship is mixed or uncertain, leave it out and
record the gap in `sources.md`. In v1, `human-rewritten` and `assistant-assisted` outcomes
are permanently excluded even when the rewrite was substantial; this avoids subjective
promotion tests and surviving assistant structure. Mark an actively disowned historical
passage `deprecated` instead of deleting its provenance.
