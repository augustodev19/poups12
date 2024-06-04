from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class QueryAuthMiddleware:
    """
    Custom middleware for WebSocket authentication using query string.
    """
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return QueryAuthMiddlewareInstance(scope, self)

class QueryAuthMiddlewareInstance:
    def __init__(self, scope, middleware):
        self.scope = scope
        self.middleware = middleware

    async def __call__(self, receive, send):
        query_string = parse_qs(self.scope['query_string'].decode())
        user_id = query_string.get('user_id')

        if user_id:
            self.scope['user'] = await get_user(user_id[0])
        else:
            self.scope['user'] = AnonymousUser()

        inner = self.middleware.inner(self.scope)
        return await inner(receive, send)