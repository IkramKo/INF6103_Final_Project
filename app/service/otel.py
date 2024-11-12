from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

class Otel:
    def __init__(self):
        metrics.set_meter_provider(MeterProvider())
        metrics.get_meter_provider().start_exporter(
            OTLPMetricExporter()  #Configure your exporter (OTLP, Prometheus, etc.)
        )
        self.meter = metrics.get_meter(__name__)