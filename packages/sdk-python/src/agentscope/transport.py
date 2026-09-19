import json, logging, socket, urllib.error, urllib.request
class HttpTransport:
    def __init__(self,endpoint,key,raise_on_error): self.url=endpoint.rstrip("/")+"/v1/ingest"; self.events_url=endpoint.rstrip("/")+"/v1/events"; self.key=key; self.raise_on_error=raise_on_error
    def send(self,payload):
        try:
            data=json.dumps(payload, allow_nan=False).encode()
            if len(data) > 2 * 1024 * 1024: raise ValueError('trace exceeds 2 MiB')
        except (ValueError, TypeError) as error:
            logging.getLogger('agentscope').warning('AgentScope rejected invalid or oversized trace')
            if self.raise_on_error: raise RuntimeError('AgentScope payload invalid or larger than 2 MiB') from error
            return
        error=None
        for _ in range(2):
            try:
                request=urllib.request.Request(self.url,data=data,headers={"Authorization":f"Bearer {self.key}","Content-Type":"application/json"},method="POST")
                with urllib.request.urlopen(request,timeout=2) as response:
                    if response.status in (200,201): return
            except urllib.error.HTTPError as exc:
                error=exc
                if exc.code not in (429,502,503,504): break
            except (urllib.error.URLError, socket.timeout) as exc: error=exc
        logging.getLogger("agentscope").warning("AgentScope could not send trace: %s", type(error).__name__)
        if self.raise_on_error: raise RuntimeError("AgentScope transport failed") from error
    def send_events(self,payload):
        data=json.dumps(payload, allow_nan=False).encode()
        request=urllib.request.Request(self.events_url,data=data,headers={"Authorization":f"Bearer {self.key}","Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(request,timeout=2) as response:
            if response.status not in (200,201): raise RuntimeError("AgentScope event transport failed")
