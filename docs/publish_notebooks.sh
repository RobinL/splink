#!/usr/bin/env bash
# Publish only notebooks from the exact Pages artifact being deployed.
set -euo pipefail

if [[ "${GITHUB_REPOSITORY:-}" != "RobinL/splink" ||
      "${GITHUB_EVENT_NAME:-}" != "push" ||
      "${GITHUB_REF:-}" != "refs/heads/master" ]]; then
    echo "Notebook publishing is restricted to master pushes in RobinL/splink" >&2
    exit 1
fi

site_dir=$(realpath "$1")
publish_dir=$(mktemp -d)
trap 'rm -rf "$publish_dir"' EXIT
git init --initial-branch=docs-notebooks "$publish_dir"
cd "$publish_dir"
git remote add origin https://github.com/RobinL/splink.git

# Preserve branch history, and never force-push.
if git ls-remote --exit-code --heads origin docs-notebooks; then
    git fetch --depth=1 origin docs-notebooks
    git reset --hard FETCH_HEAD
    git rm -r --ignore-unmatch .
else
    status=$?
    [[ "$status" == 2 ]] || exit "$status"
fi

while IFS= read -r -d '' notebook; do
    relative=${notebook#"$site_dir/"}
    mkdir -p "$(dirname "$relative")"
    cp "$notebook" "$relative"
done < <(find "$site_dir" -type f -name '*.ipynb' -print0)
if [[ -z "$(find . -name '*.ipynb' -print -quit)" ]]; then
    echo "No notebooks found in the Pages artifact" >&2
    exit 1
fi

git add .
if ! git diff --cached --quiet; then
    git -c user.name=github-actions\[bot\] \
        -c user.email=41898282+github-actions\[bot\]@users.noreply.github.com \
        commit -m "Publish notebooks from $GITHUB_SHA"
    git push origin HEAD:refs/heads/docs-notebooks
fi
