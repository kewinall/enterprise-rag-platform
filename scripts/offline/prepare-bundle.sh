#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUNDLE_DIR="${1:-${ROOT_DIR}/offline-bundle}"
OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.2:3b}"
APP_IMAGE="${APP_IMAGE:-enterprise-rag-platform:0.5.0}"
TMP_CONTAINER="enterprise-rag-offline-model-$$"

cleanup() {
  docker rm -f "${TMP_CONTAINER}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

command -v docker >/dev/null || { echo "docker is required"; exit 1; }
command -v python >/dev/null || { echo "python is required"; exit 1; }

mkdir -p "${BUNDLE_DIR}"/{images,wheels,models,config}

echo "[1/7] Build application image: ${APP_IMAGE}"
docker build -t "${APP_IMAGE}" "${ROOT_DIR}"

echo "[2/7] Pull third-party images"
while IFS= read -r image; do
  [[ -z "${image}" ]] && continue
  docker pull "${image}"
done < "${ROOT_DIR}/offline/images.txt"

echo "[3/7] Export container images"
all_images=("${APP_IMAGE}")
while IFS= read -r image; do
  [[ -z "${image}" ]] && continue
  all_images+=("${image}")
done < "${ROOT_DIR}/offline/images.txt"

for image in "${all_images[@]}"; do
  filename="$(echo "${image}" | tr '/:@' '____').tar"
  docker save -o "${BUNDLE_DIR}/images/${filename}" "${image}"
done

echo "[4/7] Download Python wheels"
python -m pip download --dest "${BUNDLE_DIR}/wheels" "${ROOT_DIR}"

echo "[5/7] Export Ollama model: ${OLLAMA_MODEL}"
docker run -d --name "${TMP_CONTAINER}" ollama/ollama:0.33.3 >/dev/null
docker exec "${TMP_CONTAINER}" ollama pull "${OLLAMA_MODEL}"
docker cp "${TMP_CONTAINER}:/root/.ollama/models" "${BUNDLE_DIR}/models/"

echo "[6/7] Copy deployment configuration"
cp "${ROOT_DIR}/docker-compose.yml" "${BUNDLE_DIR}/config/"
cp "${ROOT_DIR}/.env.example" "${BUNDLE_DIR}/config/"
cp "${ROOT_DIR}/litellm_config.yaml" "${BUNDLE_DIR}/config/"
cp "${ROOT_DIR}/otel-collector-config.yaml" "${BUNDLE_DIR}/config/"
cp -R "${ROOT_DIR}/charts" "${BUNDLE_DIR}/config/"
cp -R "${ROOT_DIR}/keycloak" "${BUNDLE_DIR}/config/"

echo "[7/7] Generate SHA-256 checksums"
(
  cd "${BUNDLE_DIR}"
  find . -type f ! -name SHA256SUMS -print0     | sort -z     | xargs -0 sha256sum > SHA256SUMS
)

echo "Offline bundle created: ${BUNDLE_DIR}"
echo "Verify before transfer: scripts/offline/verify-bundle.sh ${BUNDLE_DIR}"
