#!/usr/bin/env bash
set -e
KOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$KOK"
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
echo "core.hooksPath -> .githooks kuruldu"
