from django.shortcuts import redirect
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        current_time = timezone.now()
        last_activity = request.session.get('last_activity', current_time)
        session_expiry = timedelta(seconds=getattr(settings, 'SESSION_IDLE_TIMEOUT', 1800))

        if current_time - last_activity > session_expiry:
            logout(request)
        else:
            request.session['last_activity'] = current_time

class RestrictPageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path == '/users/login/':
            # Redirect authenticated users away from the login page
            return redirect('users/dashboard')

        response = self.get_response(request)
        return response
