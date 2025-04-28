# middleware/jwt_auth_middleware.py

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only set user if it's AnonymousUser
        if getattr(request, 'user', None) and request.user.is_authenticated:
            return self.get_response(request)

        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get('user_id')
                User = get_user_model()
                user = User.objects.get(user_id=user_id)
                request.user = user
                request._cached_user = user
            except (jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidTokenError):
                request.user = AnonymousUser()

        return self.get_response(request)
