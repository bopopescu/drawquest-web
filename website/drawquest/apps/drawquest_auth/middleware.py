from django.conf import settings

SESSION_HEADER = 'X_SESSIONID'

class SessionHeaderMiddleware(object):
    def process_request(self, request):
        session_key = request.META.get('HTTP_' + SESSION_HEADER)
        if session_key is not None:
            request.COOKIES[settings.SESSION_COOKIE_NAME] = session_key

