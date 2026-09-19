from datetime import UTC, datetime
from queue import Full, Queue
from threading import Event, Thread
from uuid import uuid4


class BackgroundExporter:
    def __init__(self, transport, limit=1000):
        self.transport, self.queue, self.dropped = transport, Queue(maxsize=limit), 0
        self.stop = Event(); self.thread = Thread(target=self._run, daemon=True); self.thread.start()
    def submit(self, event):
        try: self.queue.put_nowait(event)
        except Full: self.dropped += 1
    def _run(self):
        while not self.stop.is_set() or not self.queue.empty():
            try: event = self.queue.get(timeout=.1)
            except Exception: continue
            try: self.transport.send_events({"events": [event]})
            except Exception: pass
            finally: self.queue.task_done()
    def flush(self): self.queue.join()
    def shutdown(self): self.stop.set(); self.flush(); self.thread.join(timeout=2)


def event(kind, *, project_id, agent_name, agent_id, instance_id, execution_id, payload=None):
    return {"event_id": str(uuid4()), "schema_version": "1.0", "type": kind, "source": "agentscope-python",
        "project_id": project_id, "agent_name": agent_name, "agent_id": agent_id, "instance_id": instance_id,
        "execution_id": execution_id, "occurred_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"), "payload": payload or {}}
