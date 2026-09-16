from contextvars import ContextVar

active_span = ContextVar("agentscope_active_span", default=None)
