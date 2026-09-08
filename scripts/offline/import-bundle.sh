#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR="${1:-offline-bundle}"
OLLAMA_VOLUME="${OLLAMA_VOLUME:-enterprise-rag_ollama-data}"
TMP_CONTAINER="enterprise-rag-offline-import-$$"

cleanup() {
  docker rm -f "${TMP_CONTAINER}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

command -v docker >/dev/null || { echo "docker is required"; exit 1; }

"$(dirname "$0")/verify-bundle.sh" "${BUNDLE_DIR}"

echo "[1/3] Load container images"
for archive in "${BUNDLE_DIR}"/images/*.tar; do
  docker load -i "${archive}"
done

echo "[2/3] Restore Ollama model volume"
docker volume create "${OLLAMA_VOLUME}" >/dev/null
docker create   --name "${TMP_CONTAINER}"   -v "${OLLAMA_VOLUME}:/root/.ollama"   ollama/ollama:0.33.3 >/dev/null

if [[ -d "${BUNDLE_DIR}/models/models" ]]; then
  docker cp "${BUNDLE_DIR}/models/models" "${TMP_CONTAINER}:/root/.ollama/"
fi

echo "[3/3] Configuration bundle: ${BUNDLE_DIR}/config"
echo "Python wheels: ${BUNDLE_DIR}/wheels"
echo "Imported Ollama volume: ${OLLAMA_VOLUME}"
