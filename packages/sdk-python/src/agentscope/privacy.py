from collections.abc import Mapping


def sanitize(value, sensitive_fields=frozenset({"api_key", "authorization", "password", "secret", "token"})):
    if isinstance(value, Mapping):
        return {str(key): "[REDACTED]" if str(key).lower() in sensitive_fields else sanitize(item, sensitive_fields) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item, sensitive_fields) for item in value]
    if isinstance(value, tuple):
        return [sanitize(item, sensitive_fields) for item in value]
    return value
