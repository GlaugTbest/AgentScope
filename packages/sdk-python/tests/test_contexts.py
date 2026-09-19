from agentscope import AgentScope


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
