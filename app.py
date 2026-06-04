import time
import random
import logging

from opentelemetry.sdk.resources import Resource

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import get_meter, set_meter_provider

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter


resource = Resource.create({"service.name":"web_app"})

# Traces
provider  = TracerProvider(resource=resource)
processor = SimpleSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("tracer")

# Metrics
metricReader = PeriodicExportingMetricReader(OTLPMetricExporter())
metricProvider = MeterProvider(resource=resource, metric_readers=[metricReader])
set_meter_provider(meter_provider=metricProvider)   
meter = get_meter("meter")
counter = meter.create_counter("requests")
timer = meter.create_histogram("timer", unit="s")

# Logs
loggerProvider = LoggerProvider(resource=resource)
loggingProcessor = BatchLogRecordProcessor(OTLPLogExporter())
loggerProvider.add_log_record_processor(loggingProcessor)
LoggingHandler = LoggingHandler(logger_provider = loggerProvider) 
logging.getLogger().addHandler(LoggingHandler)       
logging.getLogger().setLevel(logging.INFO) 

def handle_request():
    with tracer.start_as_current_span("handle_request") as span:
            span.set_attribute("http.method", "GET")
            counter.add(1)
            parse()
            query_db()
            render()

def parse():
    with tracer.start_as_current_span("parse"):
        logging.info("Status: Parsing")
        time.sleep(1)

def query_db():
    with tracer.start_as_current_span("query_db"):
        logging.info("Status: Querying DB")
        
        # Simulated error 
        if random.randint(1,3) == 1:
            raise Exception("Database query failed")
        time.sleep(2)

def render():
    with tracer.start_as_current_span("render"):
        logging.info("Status: Rendering")
        time.sleep(3)


# for x in range(5):
while True:
    try:
        timestamp1 = time.time()
        handle_request()
        timestamp2 = time.time()
        timer.record(timestamp2 - timestamp1)  
    except Exception as e:
        logging.error("Error occured when handling request")