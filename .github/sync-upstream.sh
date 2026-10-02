#!/usr/bin/env bash
# Merge the latest upstream main into a fresh branch from the fork's main.
# Exit 0: no changes or a tested sync PR; nonzero: conflict, check, or API failure.
set -euo pipefail

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git fetch origin main
git fetch https://github.com/jbaruch/blog-writer.git main
upstream_sha=$(git rev-parse FETCH_HEAD)
if git merge-base --is-ancestor "$upstream_sha" origin/main; then
  echo 'Fork already contains upstream main.'
  exit 0
fi

sync_branch=automation/sync-upstream
previous_head=$(git ls-remote --heads origin "$sync_branch" | cut -f1)
git switch --create "$sync_branch" origin/main
if ! git merge --no-edit "$upstream_sha"; then
  git merge --abort
  echo 'Upstream conflicts with fork changes; resolve manually before syncing.' >&2
  exit 1
fi

# ACR bundles this metadata with the skill, outside Tessl's root layout.
cp .tessl-plugin/plugin.json skills/blog-writer/catalog-source.json
git add skills/blog-writer/catalog-source.json
if ! git diff --cached --quiet; then
  git commit -m 'chore: refresh bundled upstream catalog version'
fi

# GitHub's built-in token does not trigger pull_request workflows. Run the
# existing gates here before pushing the generated PR; never imply PR CI ran.
bash .github/install-python-gate.sh
bash .github/lint-shell.sh
bash .github/lint-python.sh
bash .github/run-script-tests.sh

git push --force-with-lease="refs/heads/$sync_branch:$previous_head" origin "$sync_branch"
body_file=$(mktemp)
trap 'rm -f "$body_file"' EXIT
cat > "$body_file" <<'BODY'
Merge the latest jbaruch/blog-writer main into this fork, preserving fork changes.

The sync workflow runs shell and Python lint plus the script tests before pushing.
GitHub's built-in token does not trigger separate pull_request workflows.
Review this PR and merge when ready; conflicts or failing gates stop the sync.
BODY
existing=$(gh pr list --repo "$GH_REPO" --head "$sync_branch" --base main --state open --json number --jq '.[0].number // empty')
if [ -n "$existing" ]; then
  gh pr edit "$existing" --repo "$GH_REPO" --body-file "$body_file"
else
  gh pr create --repo "$GH_REPO" --base main --head "$sync_branch" \
    --title 'chore: sync blog-writer upstream' --body-file "$body_file"
fi
