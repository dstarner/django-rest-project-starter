from django.http import HttpRequest, HttpResponse
from django.test import TestCase

from ..middleware import HerokuAppRedirectMiddleware


class HerokuAppRedirectMiddlewareTestCase(TestCase):

    def test_heroku_url_redirect(self):
        heroku_domain = 'someapp.herokuapp.com'
        real_domain = 'myrealwebsite.com'
        with self.settings(SERVING_ON_HEROKU=True, HEROKU_APP_DOMAIN=heroku_domain, DOMAIN=real_domain):
            request = HttpRequest()
            request.META['HTTP_HOST'] = heroku_domain
            middleware = HerokuAppRedirectMiddleware(None)
            response = middleware(request)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response.url, f'http://{real_domain}')

    def test_no_url_redirect(self):
        heroku_domain = 'someapp.herokuapp.com'
        real_domain = 'myrealwebsite.com'
        with self.settings(SERVING_ON_HEROKU=True, HEROKU_APP_DOMAIN=heroku_domain, DOMAIN=real_domain):
            request = HttpRequest()
            request.META['HTTP_HOST'] = real_domain
            middleware = HerokuAppRedirectMiddleware(lambda _: HttpResponse('hi', status=200))
            response = middleware(request)
            self.assertEqual(response.status_code, 200)
