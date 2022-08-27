from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


class HerokuAppRedirectMiddleware:
    """Redirects any Heroku-based domain requests to their actual URLs
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if settings.SERVING_ON_HEROKU and settings.HEROKU_APP_DOMAIN in request.get_host():
            return redirect(f'{request.scheme}://{settings.DOMAIN}{request.path}', permanent=True)
        response = self.get_response(request)
        return response
