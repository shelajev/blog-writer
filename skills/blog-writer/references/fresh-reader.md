# Fresh audience review

Use before delivering public prose, including a scoped non-blog assignment.
This review catches what a context-rich writer cannot see. It complements the
existing voice, accuracy, and anti-pattern checks.

1. Write a short audience brief: purpose, reader role, and knowledge the published
   piece may assume. Infer it from the assignment when clear. Do not smuggle in
   answers to gaps in the draft. If a prerequisite belongs in the piece, put it there.
2. Send the complete draft and only material actually visible to that reader.
   Exclude research banks, conversation history, persona files, private notes,
   source trees, nested helper scripts, and prior reviews. For a sequential
   tutorial, include only earlier learner-visible chapters as supporting material.
3. Run the helper with an existing Gemini credential in the current environment.
   It makes one stateless API call, supplies no tools or cached context, and loads
   no harness instructions, skills, or sessions. It reads only named UTF-8 files.

```bash
python3 .tessl/plugins/jbaruch/blog-writer/skills/blog-writer/fresh-reader.py \
  <draft.md> --audience <audience-brief.md> --output <reader-review.md>
```

Optional `--material <reader-visible.md>` repeats. `--model <gemini-model-id>`
overrides `BLOG_READER_MODEL` and the default `gemini-3.8-flash`. In a source
checkout use `skills/blog-writer/fresh-reader.py`; for ACR use the realized skill's
`fresh-reader.py` path shown by `acr realize`. Input files remain local except for
the explicit text sent to Gemini. No credentials are written or included in URLs.
The helper needs Python 3.9+ and an existing `GEMINI_API_KEY` or `GOOGLE_API_KEY`;
proxy-managed sandbox credentials work through the same API host.

Exit 0 means a complete review was saved, not that the piece passed. Read the
verdict and findings. Exit 1 means failed/incomplete review; exit 2 means missing
credential or invalid arguments. Do not report either as a successful review or
create new credentials. Report the missing review and continue only as explicitly
unreviewed work.

Fix missing premises, unclear instructions, order, and unsupported references.
Put essential explanations where readers encounter the problem: mentioning a
script three layers down does not give a human its inputs, effects, or next step.
Preserve author intent. In review-only work, propose fixes without editing.
After substantive repairs, run a new call on the revised draft without the earlier
review. Resolve blockers or disclose them; optional style preferences are judgment
calls. Report audience-review status separately from accuracy and runtime checks.
