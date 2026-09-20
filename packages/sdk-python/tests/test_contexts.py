import asyncio
from threading import Event
from urllib.error import URLError

from agentscope import AgentScope
from agentscope.events import BackgroundExporter


class Transport:
    def __init__(self): self.payloads = []
    def send(self, payload): self.payloads.append(payload)


class IncrementalTransport(Transport):
    def __init__(self): super().__init__(); self.events = []
    def send_events(self, payload): self.events.extend(payload["events"])


def test_nested_spans_receive_parent_and_send_when_trace_ends():
    transport = Transport()
    scope = AgentScope(transport=transport, capture_content=True)
    with scope.trace("agent") as trace:
        with trace.span(type="custom", name="outer") as outer:
            outer.set_input({"a": 1})
            with trace.span(type="tool", name="inner"):
                pass
    spans = transport.payloads[0]["spans"]
    assert spans[1]["parent_span_id"] == spans[0]["span_id"]
    assert spans[0]["input"] == {"a": 1}


def test_original_exception_is_propagated_and_recorded():
    transport = Transport()
    scope = AgentScope(transport=transport)
    error = ValueError("boom")
    try:
        with scope.trace("agent") as trace:
            with trace.span(type="tool", name="broken"):
                raise error
    except ValueError as caught:
        assert caught is error
    assert transport.payloads[0]["spans"][0]["status"] == "error"


def test_incremental_events_are_exported_without_changing_trace_batch():
    transport = IncrementalTransport()
    scope = AgentScope(transport=transport)
    with scope.trace("agent") as trace:
        trace.activity("Consultando documentos", completed=2)
        with trace.span(type="tool", name="search"):
            pass
    scope.flush()
    assert transport.payloads[0]["trace"]["agent_name"] == "agent"
    assert [event["type"] for event in transport.events] == [
        "execution.started", "activity.updated", "span.started", "span.ended", "execution.completed"
    ]
    scope.shutdown()


def test_exporter_retries_retryable_failures_and_exposes_diagnostics():
    class FlakyTransport:
        def __init__(self): self.calls = 0; self.events = []
        def send_events(self, payload):
            self.calls += 1
            if self.calls < 3: raise URLError('offline')
            self.events.extend(payload['events'])

    transport = FlakyTransport()
    exporter = BackgroundExporter(transport, batch_size=10, max_retries=3, sleeper=lambda _: None)
    assert exporter.submit({'event_id': 'one'})
    assert exporter.submit({'event_id': 'two'})
    assert exporter.flush(timeout=1)
    assert [item['event_id'] for item in transport.events] == ['one', 'two']
    assert exporter.diagnostics == {'enqueued': 2, 'exported': 2, 'dropped': 0, 'failed': 0, 'retries': 2, 'pending': 0}
    assert exporter.shutdown()


def test_exporter_drops_when_the_bounded_buffer_is_full():
    entered, release = Event(), Event()

    class BlockingTransport:
        def send_events(self, payload):
            entered.set()
            release.wait(1)

    exporter = BackgroundExporter(BlockingTransport(), limit=1, batch_size=1)
    assert exporter.submit({'event_id': 'first'})
    assert entered.wait(1)
    assert exporter.submit({'event_id': 'second'})
    assert not exporter.submit({'event_id': 'dropped'})
    release.set()
    assert exporter.flush(timeout=1)
    assert exporter.diagnostics['dropped'] == 1
    assert exporter.shutdown()


def test_async_contexts_preserve_the_existing_trace_contract():
    transport = IncrementalTransport()
    scope = AgentScope(transport=transport)

    async def instrumented_work():
        async with scope.trace('async-agent') as trace:
            async with trace.span(type='tool', name='async-search'):
                await asyncio.sleep(0)

    asyncio.run(instrumented_work())
    scope.flush()
    assert transport.payloads[0]['trace']['agent_name'] == 'async-agent'
    assert transport.payloads[0]['spans'][0]['name'] == 'async-search'
    assert scope.diagnostics['exported'] == 4
    scope.shutdown()


def test_sensitive_content_is_sanitized_before_trace_and_event_export():
    transport = IncrementalTransport()
    scope = AgentScope(transport=transport, capture_content=True)
    with scope.trace('agent', metadata={'token': 'trace-secret'}) as trace:
        trace.activity('Working', authorization='Bearer secret')
        with trace.span(type='tool', name='search', metadata={'password': 'hidden'}) as span:
            span.set_input({'api_key': 'input-secret', 'safe': 'kept'})
    scope.flush()
    payload = transport.payloads[0]
    assert payload['trace']['metadata']['token'] == '[REDACTED]'
    assert payload['spans'][0]['metadata']['password'] == '[REDACTED]'
    assert payload['spans'][0]['input'] == {'api_key': '[REDACTED]', 'safe': 'kept'}
    assert transport.events[1]['payload']['authorization'] == '[REDACTED]'
    scope.shutdown()
