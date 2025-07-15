import os
import django

# Setup Django before importing models or settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  
django.setup()

from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"].decode()
        token = parse_qs(query_string).get("token")
        
        if token:
            try:
                validated_token = UntypedToken(token[0])
                jwt_auth = JWTAuthentication()
                user = await database_sync_to_async(jwt_auth.get_user)(validated_token)
                scope["user"] = user
            except Exception:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
