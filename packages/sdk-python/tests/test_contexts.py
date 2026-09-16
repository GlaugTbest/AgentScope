from agentscope import AgentScope


class Transport:
    def __init__(self): self.payloads = []
    def send(self, payload): self.payloads.append(payload)


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
