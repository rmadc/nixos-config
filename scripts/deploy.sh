#!/usr/bin/env bash
set -euo pipefail

main() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "Run this script with sudo: sudo $0" >&2
    return 1
  fi

  local repo_dir host status revision
  repo_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
  host=$(hostname -s)

  if [ -z "$host" ]; then
    echo "Could not determine the short hostname." >&2
    return 1
  fi
  status=$(git -C "$repo_dir" status --porcelain)
  if [ -n "$status" ]; then
    echo "The repository has uncommitted or untracked changes; review them before deploying." >&2
    return 1
  fi

  echo "Updating the current branch (fast-forward only)..."
  git -C "$repo_dir" pull --ff-only
  revision=$(git -C "$repo_dir" rev-parse HEAD)
  printf 'Deploying %s for %s from %s\n' "$revision" "$host" "$repo_dir"
  exec nixos-rebuild switch --flake "$repo_dir#$host"
}

main "$@"
