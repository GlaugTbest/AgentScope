from starlette.responses import JSONResponse


class BodyLimitMiddleware:
    """Bound buffering before JSON parsing, including chunked requests."""
    def __init__(self, app, limit=2 * 1024 * 1024):
        self.app, self.limit = app, limit

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] not in ('POST', 'PUT', 'PATCH'):
            return await self.app(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect': return
            chunk = message.get('body', b'')
            size += len(chunk)
            if size > self.limit:
                return await JSONResponse({'detail': 'request too large'}, 413)(scope, receive, send)
            chunks.append(chunk)
            if not message.get('more_body', False): break
        delivered = False
        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type': 'http.request', 'body': b''.join(chunks), 'more_body': False}
            return await receive()
        await self.app(scope, replay, send)
