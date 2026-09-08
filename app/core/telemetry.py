import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from app.core.config import get_settings

logger = logging.getLogger(__name__)
_initialized = False


def setup_telemetry() -> None:
    global _initialized

    settings = get_settings()
    if _initialized or not settings.otel_enabled:
        return

    resource = Resource.create(
        {
            "service.name": settings.otel_service_name,
            "service.version": settings.app_version,
            "deployment.environment": settings.app_env,
        }
    )
    provider = TracerProvider(resource=resource)

    if settings.otel_exporter_otlp_traces_endpoint:
        exporter = OTLPSpanExporter(
            endpoint=settings.otel_exporter_otlp_traces_endpoint,
        )
    else:
        exporter = ConsoleSpanExporter()

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    _initialized = True
    logger.info("OpenTelemetry tracing enabled for %s", settings.otel_service_name)


def get_tracer(name: str):
    return trace.get_tracer(name)
