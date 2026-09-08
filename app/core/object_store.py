import asyncio
import logging
import re
from functools import lru_cache
from pathlib import PurePath

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _safe_name(value: str) -> str:
    name = PurePath(value).name or "document"
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


class ObjectStore:
    def __init__(self) -> None:
        self.client = None
        self.available = False

    def _build_client(self):
        settings = get_settings()
        return boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url or None,
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
        )

    def _ensure_bucket(self) -> None:
        settings = get_settings()
        client = self._build_client()
        try:
            client.head_bucket(Bucket=settings.s3_bucket)
        except ClientError as exc:
            error_code = str(exc.response.get("Error", {}).get("Code", ""))
            if error_code not in {"404", "NoSuchBucket", "NotFound"}:
                raise
            kwargs = {"Bucket": settings.s3_bucket}
            if settings.s3_region != "us-east-1" and not settings.s3_endpoint_url:
                kwargs["CreateBucketConfiguration"] = {
                    "LocationConstraint": settings.s3_region
                }
            client.create_bucket(**kwargs)
        self.client = client

    async def start(self) -> None:
        settings = get_settings()
        if not settings.object_store_enabled:
            return
        try:
            await asyncio.to_thread(self._ensure_bucket)
        except (BotoCoreError, ClientError, OSError) as exc:
            logger.warning("Object store unavailable: %s", exc)
            self.available = False
            return
        self.available = True
        logger.info("Object store enabled: bucket=%s", settings.s3_bucket)

    def make_object_key(self, tenant_id: str, document_id: str, source: str) -> str:
        return f"{tenant_id}/{document_id}/{_safe_name(source)}"

    async def put_document(
        self,
        tenant_id: str,
        document_id: str,
        source: str,
        payload: bytes,
        content_type: str | None,
    ) -> str:
        settings = get_settings()
        if not settings.object_store_enabled:
            return ""
        if self.client is None or not self.available:
            raise RuntimeError("Object store is not available")

        object_key = self.make_object_key(tenant_id, document_id, source)
        kwargs = {
            "Bucket": settings.s3_bucket,
            "Key": object_key,
            "Body": payload,
        }
        if content_type:
            kwargs["ContentType"] = content_type
        await asyncio.to_thread(self.client.put_object, **kwargs)
        return object_key

    async def delete_object(self, object_key: str | None) -> None:
        settings = get_settings()
        if not object_key or not settings.object_store_enabled:
            return
        if self.client is None or not self.available:
            raise RuntimeError("Object store is not available")
        await asyncio.to_thread(
            self.client.delete_object,
            Bucket=settings.s3_bucket,
            Key=object_key,
        )

    async def presigned_download_url(
        self,
        object_key: str,
        expires_seconds: int = 300,
    ) -> str:
        settings = get_settings()
        if self.client is None or not self.available:
            raise RuntimeError("Object store is not available")
        return await asyncio.to_thread(
            self.client.generate_presigned_url,
            "get_object",
            Params={"Bucket": settings.s3_bucket, "Key": object_key},
            ExpiresIn=expires_seconds,
        )


@lru_cache
def get_object_store() -> ObjectStore:
    return ObjectStore()
