from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import get_tracer

app = Flask(__name__)

# Initialize the TracerProvider and set the Jaeger exporter
trace.set_tracer_provider(TracerProvider())
tracer = get_tracer(__name__)
jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask app for tracing
FlaskInstrumentor().instrument_app(app)

@app.route('/')
def hello_world():
    with tracer.start_as_current_span("hello"):
        return 'Hello, World!'

if __name__ == '__main__':
    app.run()
