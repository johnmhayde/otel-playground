import json
import logging
import time
import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (OTLPLogExporter)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (OTLPSpanExporter)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


# Shared OpenTelemetry resource
resource = Resource.create(
    {
        "service.name": os.getenv("OTEL_SERVICE_NAME"),
        "service.version": "1.0.0",
        "deployment.environment": "local",
    }
)

# Tracing
trace_provider = TracerProvider(resource=resource)
trace_exporter = OTLPSpanExporter()
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer("fastapi-otel-demo")

# Logging
logger_provider = LoggerProvider(resource=resource,)
log_exporter = OTLPLogExporter()
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
set_logger_provider(logger_provider)

# Send standard Python logging records into OpenTelemetry.
otel_handler = LoggingHandler(
    level=logging.INFO,
    logger_provider=logger_provider,
)

# Application logger
logger = logging.getLogger("fastapi-demo")
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(otel_handler)
logger.propagate = False

# FastAPI init
app = FastAPI(title="FastAPI OpenTelemetry Demo")
FastAPIInstrumentor.instrument_app(app)

# Logging helper
def log_json(message: str, **attributes):
    log_body = {"message": message, **attributes}
    logger.info(json.dumps(log_body),extra=attributes)

# Endpoints
@app.get("/")
async def root():
    log_json(
        "Root endpoint called",
        endpoint="/",
    )
    return {
        "service": "fastapi-otel-demo",
        "status": "ok",
    }


@app.get("/process/{item_id}")
async def process_item(item_id: str):
    log_json(
        f"Starting processing item: {item_id}",
        endpoint="/process/{item_id}",
    )
    # Dummy Kafka read
    with tracer.start_as_current_span("kafka read") as span:
        span.set_attribute("messaging.system","kafka")
        span.set_attribute("messaging.destination.name","orders")
        span.set_attribute("messaging.operation.type","receive")
        span.set_attribute("item.id",item_id)
        log_json(
            "Reading item from Kafka",
            item_id=item_id,
            topic="orders",
        )
        # Simulate Kafka work
        time.sleep(0.1)
        span.add_event(
            "kafka message received",
            {
                "item.id": item_id,
            },
        )
        log_json("Kafka read completed",item_id=item_id)

    # Dummy DB write
    with tracer.start_as_current_span("db write") as span:
        span.set_attribute(
            "db.system",
            "postgresql",
        )
        span.set_attribute(
            "db.operation.name",
            "INSERT",
        )
        span.set_attribute(
            "db.table.name",
            "orders",
        )
        span.set_attribute(
            "item.id",
            item_id,
        )
        log_json(
            "Writing item to database",
            item_id=item_id,
            table="orders",
        )
        # Simulate database work
        time.sleep(0.15)
        span.add_event(
            "database write completed",
            {
                "item.id": item_id,
            },
        )
        log_json(
            "Database write completed",
            item_id=item_id,
        )

    log_json(
        f"Finished processing item: {item_id}",
        status="success",
    )

    return {
        "item_id": item_id,
        "status": "processed",
    }
