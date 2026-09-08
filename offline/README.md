# 離線部署 Bundle / Offline Deployment Bundle

## 目的 / Purpose

**繁體中文**  
此流程用於有 Internet 的 Staging Zone 先下載 Application Image、第三方 Container Images、Python Wheels 與 Ollama Model，再產生 SHA-256 Checksum，攜入 Air-Gapped Environment 後驗證並匯入。

**English**  
This workflow prepares the application image, third-party container images, Python wheels, and an Ollama model in an internet-connected staging zone, generates SHA-256 checksums, and then verifies/imports the bundle in an air-gapped environment.

## 建立 / Prepare

    OLLAMA_MODEL=llama3.2:3b scripts/offline/prepare-bundle.sh ./offline-bundle

## 驗證 / Verify

    scripts/offline/verify-bundle.sh ./offline-bundle

## 匯入 / Import

    scripts/offline/import-bundle.sh ./offline-bundle

## Bundle Structure

    offline-bundle/
    ├── images/
    ├── wheels/
    ├── models/
    ├── config/
    └── SHA256SUMS

## Security Notes / 安全注意

**繁體中文**
- 攜入前應再次執行 Trivy Image Scan 與 SBOM 產出。
- minio/minio:latest 僅供 Demo；正式 Offline Release 應先解析並固定 Image Digest。
- .env.example 不含真實 Secret；離線環境必須重新建立 Secret。
- Checksum 用於完整性確認，不等同 Code Signing。

**English**
- Re-run Trivy image scans and generate SBOMs before transfer.
- minio/minio:latest is for the demo; production offline releases should resolve and pin an image digest.
- .env.example contains no real secrets; recreate secrets inside the offline environment.
- Checksums provide integrity verification but are not a substitute for code signing.
