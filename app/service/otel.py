from app.meta.singleton import Singleton
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

import logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

class Otel(metaclass=Singleton):
    def __init__(self):
        metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(insecure=True))
        provider = MeterProvider(metric_readers=[metric_reader])
        metrics.set_meter_provider(provider)
        self.meter = metrics.get_meter("inf6103.simulation")

        logger_provider = LoggerProvider()
        set_logger_provider(logger_provider)
        exporter = OTLPLogExporter(
            insecure=True
        )
        logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to see detailed information
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
        handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
        logging.getLogger().addHandler(handler)
