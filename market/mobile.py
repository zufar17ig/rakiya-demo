"""Bearer-authenticated native API. Browser APIs retain Django CSRF protection."""
import json
import re
from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .views import api

@csrf_exempt
def mobile_api(request, action):
    # Never authenticate native requests with ambient browser cookies. Only an
    # explicit, unguessable session key in Authorization is accepted here.
    authorization = request.headers.get('Authorization', '')
    key = authorization[7:] if authorization.startswith('Bearer ') else None
    if authorization and (not key or not re.fullmatch(r'[a-z0-9]{32}', key)):
        return JsonResponse({'error': 'Invalid session. Please sign in again.'}, status=401)
    request.session = SessionStore(session_key=key)
    request.user = get_user(request) if key else AnonymousUser()
    public = action in ['state', 'jobs', 'login', 'register']
    if (key and not request.user.is_authenticated) or (not public and not request.user.is_authenticated):
        return JsonResponse({'error': 'Session expired. Please sign in again.'}, status=401)
    response = api(request, action)
    if action in ['login', 'register'] and request.method == 'POST' and response.status_code == 200:
        request.session.save()
        payload = json.loads(response.content)
        payload['token'] = request.session.session_key
        response = JsonResponse(payload)
    response['Cache-Control'] = 'no-store'
    response['Pragma'] = 'no-cache'
    return response
