from datetime import UTC, datetime
from collections import defaultdict
from ..schemas import IngestBatch


def _value(value):
    for key in ("stringValue", "intValue", "doubleValue", "boolValue"):
        if key in value: return value[key]
    return None


def _attributes(items):
    return {item["key"]: _value(item.get("value", {})) for item in items if "key" in item}


def _timestamp(value):
    return datetime.fromtimestamp(int(value) / 1_000_000_000, UTC).isoformat().replace("+00:00", "Z")


def batches(payload):
    grouped = defaultdict(list)
    for resource_span in payload.get("resourceSpans", []):
        resource = _attributes(resource_span.get("resource", {}).get("attributes", []))
        for scope_span in resource_span.get("scopeSpans", []):
            scope = _attributes(scope_span.get("scope", {}).get("attributes", []))
            for span in scope_span.get("spans", []): grouped[span.get("traceId")].append((span, resource, scope))
    result = []
    for trace_id, entries in grouped.items():
        if not trace_id: continue
        spans, starts, ends = [], [], []
        agent_name = entries[0][1].get("service.name") or "otlp-agent"
        for span, resource, scope in entries:
            start, end = _timestamp(span["startTimeUnixNano"]), _timestamp(span["endTimeUnixNano"])
            starts.append(start); ends.append(end)
            attributes = {**resource, **scope, **_attributes(span.get("attributes", []))}
            error = span.get("status", {}).get("code") == 2
            spans.append({"span_id": span["spanId"], "trace_id": trace_id, "parent_span_id": span.get("parentSpanId") or None, "type": attributes.get("gen_ai.operation.name") or "otlp", "name": span.get("name", "otlp-span"), "start_time": start, "end_time": end, "status": "error" if error else "success", "model": attributes.get("gen_ai.request.model"), "provider": attributes.get("gen_ai.provider.name"), "input_tokens": int(attributes.get("gen_ai.usage.input_tokens") or 0), "output_tokens": int(attributes.get("gen_ai.usage.output_tokens") or 0), "estimated_cost": "0", "metadata": attributes, "error": {"type": "OTLPError", "message": span.get("status", {}).get("message") or "OTLP span error"} if error else None})
        result.append(IngestBatch.model_validate({"trace": {"trace_id": trace_id, "agent_name": agent_name, "start_time": min(starts), "end_time": max(ends), "status": "error" if any(span["status"] == "error" for span in spans) else "success", "metadata": {"agentscope.source": "otlp"}, "error": None}, "spans": spans}))
    return result
