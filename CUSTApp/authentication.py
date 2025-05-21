# authentication.py
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.conf import settings
import jwt

User = get_user_model()

class HybridAuthBackend(ModelBackend):
    """
    Authentication backend that supports both password and JWT token
    authentication depending on the context
    """
    
    def authenticate(self, request=None, username=None, password=None, token=None, **kwargs):
        # If token is provided, try JWT authentication
        if token:
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                user_id = payload.get('user_id')
                
                if user_id is None:
                    return None
                    
                user = User.objects.get(user_id=user_id)
                return user
            except (jwt.PyJWTError, User.DoesNotExist):
                return None
        
        # Otherwise try standard password authentication (for admin)
        elif username and password:
            return super().authenticate(request, username, password, **kwargs)
            
        return None