# MinIO / S3 Object Storage

## 目的 / Purpose

**繁體中文**  
v0.4 將原始 Upload Document 保存至 S3-compatible Object Storage；Qdrant 只保存 Chunk 與 Metadata，不再是唯一文件來源。

**English**  
v0.4 stores original uploaded documents in S3-compatible object storage. Qdrant stores chunks and metadata but is no longer the only document representation.

## Default Demo

Docker Compose 使用 MinIO：

    http://localhost:9000

Console:

    http://localhost:9001

設定 / Configuration:

    OBJECT_STORE_ENABLED=true
    S3_ENDPOINT_URL=http://minio:9000
    S3_REGION=us-east-1
    S3_BUCKET=enterprise-rag

## Object Key

格式 / Format:

    {tenant_id}/{document_id}/{sanitized_filename}

這讓 Object Storage 與 Vector Metadata 使用同一 Tenant Boundary。  
This keeps object storage aligned with the same tenant boundary as vector metadata.

## Download

API:

    GET /api/v1/documents/{document_id}/download

**繁體中文**  
API 先驗證使用者 Tenant 與 Role，再產生短效 Presigned URL。Client 不會直接取得 Object Store Credential。

**English**  
The API validates tenant and role before issuing a short-lived presigned URL. Clients never receive object-store credentials directly.

## Production Recommendation / 正式環境建議

- MinIO Cluster 或 Cloud S3 / managed S3-compatible storage
- Bucket Encryption / KMS
- Private Endpoint / NetworkPolicy
- Versioning
- Lifecycle Policy
- Malware Scan
- Object Lock（若稽核需求需要 / when compliance requires it）
- Credential from Secret Manager
