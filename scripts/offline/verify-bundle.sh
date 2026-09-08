#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR="${1:-offline-bundle}"

[[ -f "${BUNDLE_DIR}/SHA256SUMS" ]] || {
  echo "SHA256SUMS not found in ${BUNDLE_DIR}"
  exit 1
}

(
  cd "${BUNDLE_DIR}"
  sha256sum -c SHA256SUMS
)
