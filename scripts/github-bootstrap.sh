#!/usr/bin/env bash
# One-shot: create the GitHub repo, push all branches, set API_TOKEN secret,
# and watch the first pipeline run. Re-running is safe.
#
# Prereqs (one-time):
#   1. winget install --id GitHub.cli      (already done if gh is on PATH)
#   2. gh auth login                       (interactive, needs your browser)
#
# Usage:
#   API_TOKEN=$(openssl rand -hex 16) bash scripts/github-bootstrap.sh [repo-name]
#
# Defaults:
#   repo-name = securemlops
#   visibility = public
set -euo pipefail

REPO_NAME="${1:-securemlops}"
VISIBILITY="${VISIBILITY:-public}"
API_TOKEN="${API_TOKEN:-$(openssl rand -hex 16 2>/dev/null || echo "change-me-$(date +%s)")}"

cd "$(dirname "$0")/.."

if ! command -v gh >/dev/null 2>&1; then
  if [[ -x "/c/Program Files/GitHub CLI/gh.exe" ]]; then
    GH="/c/Program Files/GitHub CLI/gh.exe"
  else
    echo "gh CLI not found. Install with: winget install --id GitHub.cli" >&2
    exit 1
  fi
else
  GH="gh"
fi

if ! "$GH" auth status >/dev/null 2>&1; then
  echo "Not authenticated. Run: gh auth login" >&2
  exit 1
fi

OWNER="$("$GH" api user --jq .login)"
echo "Authenticated as: $OWNER"

if "$GH" repo view "$OWNER/$REPO_NAME" >/dev/null 2>&1; then
  echo "Repo $OWNER/$REPO_NAME already exists; skipping create."
else
  echo "Creating repo $OWNER/$REPO_NAME ($VISIBILITY)..."
  "$GH" repo create "$REPO_NAME" --"$VISIBILITY" --source . --remote origin --disable-wiki
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "https://github.com/$OWNER/$REPO_NAME.git"
fi

echo "Pushing all branches..."
git push -u origin main
git push origin develop || true
git push origin feature/devops-enhancement || true

echo "Setting API_TOKEN repo secret (value not echoed)..."
printf '%s' "$API_TOKEN" | "$GH" secret set API_TOKEN --repo "$OWNER/$REPO_NAME" --body -

echo
echo "Done."
echo "  Repo:     https://github.com/$OWNER/$REPO_NAME"
echo "  Actions:  https://github.com/$OWNER/$REPO_NAME/actions"
echo
echo "Watching the latest workflow run (Ctrl+C to detach)..."
sleep 4
RUN_ID="$("$GH" run list --repo "$OWNER/$REPO_NAME" --branch main --limit 1 --json databaseId --jq '.[0].databaseId' || true)"
if [[ -n "${RUN_ID:-}" ]]; then
  "$GH" run watch "$RUN_ID" --repo "$OWNER/$REPO_NAME" || true
fi
