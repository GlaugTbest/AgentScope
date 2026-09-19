from __future__ import annotations

from datetime import UTC, datetime
from queue import Empty, Full, Queue
from random import random
from threading import Event, Lock, Thread
from time import monotonic, sleep
from urllib.error import HTTPError, URLError
from uuid import uuid4


class BackgroundExporter:
    """Best-effort background export that never interrupts an instrumented app."""

    def __init__(self, transport, limit=1000, batch_size=100, flush_interval=0.2,
                 max_retries=3, sleeper=sleep, random_source=random):
        if limit < 1 or batch_size < 1 or max_retries < 0:
            raise ValueError("exporter limits must be positive")
        self.transport = transport
        self.queue = Queue(maxsize=limit)
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_retries = max_retries
        self._sleep = sleeper
        self._random = random_source
        self._stopping = Event()
        self._lock = Lock()
        self._stats = {"enqueued": 0, "exported": 0, "dropped": 0, "failed": 0, "retries": 0}
        self.thread = Thread(target=self._run, name="agentscope-exporter", daemon=True)
        self.thread.start()

    def submit(self, item):
        if self._stopping.is_set():
            self._increment("dropped")
            return False
        try:
            self.queue.put_nowait(item)
            self._increment("enqueued")
            return True
        except Full:
            self._increment("dropped")
            return False

    @property
    def diagnostics(self):
        with self._lock:
            return {**self._stats, "pending": self.queue.unfinished_tasks}

    def _increment(self, key, amount=1):
        with self._lock:
            self._stats[key] += amount

    def _take_batch(self):
        try:
            batch = [self.queue.get(timeout=self.flush_interval)]
        except Empty:
            return []
        while len(batch) < self.batch_size:
            try:
                batch.append(self.queue.get_nowait())
            except Empty:
                break
        return batch

    def _run(self):
        while not self._stopping.is_set() or not self.queue.empty():
            batch = self._take_batch()
            if not batch:
                continue
            self._export(batch)
            for _ in batch:
                self.queue.task_done()

    def _export(self, batch):
        for attempt in range(self.max_retries + 1):
            try:
                self.transport.send_events({"events": batch})
                self._increment("exported", len(batch))
                return
            except Exception as error:
                if attempt >= self.max_retries or not self._retryable(error):
                    self._increment("failed", len(batch))
                    return
                self._increment("retries")
                self._sleep(self._backoff(attempt, error))

    def _backoff(self, attempt, error):
        retry_after = None
        if isinstance(error, HTTPError):
            try:
                retry_after = float(error.headers.get("Retry-After"))
            except (AttributeError, TypeError, ValueError):
                retry_after = None
        if retry_after is not None and 0 <= retry_after <= 30:
            return retry_after
        return min(2.0, 0.1 * (2 ** attempt)) + (self._random() * 0.05)

    @staticmethod
    def _retryable(error):
        if isinstance(error, (ValueError, TypeError)):
            return False
        if isinstance(error, HTTPError):
            return error.code in (429, 502, 503, 504)
        return isinstance(error, (URLError, TimeoutError, OSError, RuntimeError))

    def flush(self, timeout=None):
        deadline = monotonic() + timeout if timeout is not None else None
        with self.queue.all_tasks_done:
            while self.queue.unfinished_tasks:
                if deadline is None:
                    self.queue.all_tasks_done.wait()
                    continue
                remaining = deadline - monotonic()
                if remaining <= 0:
                    return False
                self.queue.all_tasks_done.wait(remaining)
        return True

    def shutdown(self, timeout=2):
        self._stopping.set()
        completed = self.flush(timeout)
        self.thread.join(timeout=max(0, timeout))
        return completed and not self.thread.is_alive()


def event(kind, *, project_id, agent_name, agent_id, instance_id, execution_id, payload=None):
    return {"event_id": str(uuid4()), "schema_version": "1.0", "type": kind, "source": "agentscope-python",
        "project_id": project_id, "agent_name": agent_name, "agent_id": agent_id, "instance_id": instance_id,
        "execution_id": execution_id, "occurred_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"), "payload": payload or {}}
