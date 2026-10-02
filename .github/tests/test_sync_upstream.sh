#!/usr/bin/env bash
# Verify real merges against local remotes; fake only GitHub transport and gates.
set -euo pipefail
script=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/sync-upstream.sh
fixture=$(mktemp -d)
trap 'rm -rf "$fixture"' EXIT
export SYNC_TEST_GIT
SYNC_TEST_GIT=$(command -v git)
export SYNC_TEST_ROOT="$fixture"
mkdir -p "$fixture/bin"
cat > "$fixture/bin/git" <<'GIT'
#!/usr/bin/env bash
if [ "$1" = fetch ] && [ "$2" = https://github.com/jbaruch/blog-writer.git ]; then
  exec "$SYNC_TEST_GIT" fetch "$SYNC_TEST_ROOT/upstream" main
fi
exec "$SYNC_TEST_GIT" "$@"
GIT
cat > "$fixture/bin/gh" <<'GH'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$SYNC_TEST_ROOT/gh-calls"
if [ "$1 $2" = 'pr list' ]; then
  printf '%s' "${SYNC_TEST_EXISTING:-}"
fi
GH
chmod +x "$fixture/bin/git" "$fixture/bin/gh"
export PATH="$fixture/bin:$PATH" GH_REPO=example/fork
git init --quiet --initial-branch=main "$fixture/upstream"
git -C "$fixture/upstream" config user.name fixture
git -C "$fixture/upstream" config user.email fixture@example.invalid
mkdir -p "$fixture/upstream/.github" "$fixture/upstream/.tessl-plugin" "$fixture/upstream/skills/blog-writer"
printf '{"name":"jbaruch/blog-writer","version":"1.0.0"}\n' > "$fixture/upstream/.tessl-plugin/plugin.json"
for gate in install-python-gate lint-shell lint-python run-script-tests; do
  printf '#!/bin/sh\nexit 0\n' > "$fixture/upstream/.github/$gate.sh"
done
printf 'original\n' > "$fixture/upstream/article.md"
git -C "$fixture/upstream" add .
git -C "$fixture/upstream" commit --quiet -m initial
git clone --quiet --bare "$fixture/upstream" "$fixture/fork.git"
git clone --quiet "$fixture/fork.git" "$fixture/work"
cd "$fixture/work"
bash "$script"
[ ! -f "$fixture/gh-calls" ]
printf 'new content\n' > "$fixture/upstream/new.md"
git -C "$fixture/upstream" add .
git -C "$fixture/upstream" commit --quiet -m update
bash "$script"
git --git-dir="$fixture/fork.git" show automation/sync-upstream:new.md | grep -q 'new content'
grep -q 'pr create' "$fixture/gh-calls"
git switch main
git branch -D automation/sync-upstream
SYNC_TEST_EXISTING=7 bash "$script"
grep -q 'pr edit 7' "$fixture/gh-calls"
git switch main
git branch -D automation/sync-upstream
printf 'fork edit\n' > article.md
git add article.md
git commit --quiet -m fork-change
git push --quiet origin main
before=$(git --git-dir="$fixture/fork.git" rev-parse main)
printf 'upstream edit\n' > "$fixture/upstream/article.md"
git -C "$fixture/upstream" add .
git -C "$fixture/upstream" commit --quiet -m conflict
if bash "$script"; then
  echo 'Expected conflict to stop sync' >&2
  exit 1
fi
[ "$before" = "$(git --git-dir="$fixture/fork.git" rev-parse main)" ]
printf 'Upstream sync fixture cases passed\n'
