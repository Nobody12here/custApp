# decorators.py
from functools import wraps
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponseRedirect
from django.urls import reverse

def jwt_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        jwt_authenticator = JWTAuthentication()
        
        try:
            header = request.META.get('HTTP_AUTHORIZATION', '')
            if not header.startswith('Bearer '):
                return HttpResponseRedirect(reverse('login'))
            
            token = header.split(' ')[1]
            validated_token = jwt_authenticator.get_validated_token(token)
            user = jwt_authenticator.get_user(validated_token)
            
            # Add user to request
            request.user = user
            return view_func(request, *args, **kwargs)
            
        except Exception:
            return HttpResponseRedirect(reverse('login'))
            
    return wrapped_view