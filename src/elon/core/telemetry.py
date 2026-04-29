"""OpenTelemetry init. Best-effort: if exporter env isn't set, falls back to no-op.

Env:
  OTEL_EXPORTER_OTLP_ENDPOINT  e.g. http://otelcol:4318
  OTEL_SERVICE_NAME            default "elon-api"
"""

from __future__ import annotations

import os

from elon.core.logging import get_logger

log = get_logger(__name__)


def init_otel(service: str = "elon-api") -> None:
    if not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        log.info("otel_disabled_no_endpoint")
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(resource=Resource.create({
            "service.name": os.getenv("OTEL_SERVICE_NAME", service),
        }))
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(provider)

        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from elon.core.db import engine

        try:
            SQLAlchemyInstrumentor().instrument(engine=engine)
        except Exception:
            pass
        # FastAPI instrumentation is applied by main.py via FastAPIInstrumentor.
        FastAPIInstrumentor()
    except Exception as e:
        log.warning("otel_init_failed", error=str(e))
