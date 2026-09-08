# 封閉網路部署 / Air-Gapped Deployment

## Flow / 流程

    Internet-connected Staging Zone
              |
              v
       Build / Pull / Download
              |
              v
     Container Images + Wheels
       + Ollama Model + Config
              |
              v
        SHA-256 Verification
              X
              X  Air Gap
              X
              v
        Offline Environment
              |
              v
          Verify + Import
              |
              v
             Deploy

## Prepare

    bash scripts/offline/prepare-bundle.sh ./offline-bundle

Optional:

    OLLAMA_MODEL=llama3.2:3b       bash scripts/offline/prepare-bundle.sh ./offline-bundle

## Verify

    bash scripts/offline/verify-bundle.sh ./offline-bundle

## Import

    bash scripts/offline/import-bundle.sh ./offline-bundle

## Included Content

- Application Container Image
- Third-party Runtime Images
- Python Wheels
- Ollama Model Files
- Docker Compose Config
- Helm Chart
- Keycloak Demo Realm
- SHA-256 Checksums

## Enterprise Controls / 企業控制

**繁體中文**
- Staging Zone 執行 Trivy Image Scan。
- 產出 SBOM。
- 對 Offline Release 建立 Release Manifest / Approval Record。
- 正式環境應固定 Image Digest，不使用 latest。
- 以簽章補強 SHA-256 Checksum。
- Secret 不進 Bundle，於 Offline Environment 重新建立。

**English**
- Run Trivy image scans in the staging zone.
- Generate SBOMs.
- Maintain a release manifest and approval record.
- Pin image digests for production offline releases instead of using latest.
- Add signing in addition to SHA-256 integrity checks.
- Do not place real secrets in the bundle; recreate them inside the offline environment.
