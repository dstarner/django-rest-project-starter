from types import FunctionType
from unittest import mock

from django.test import TestCase

from ..honeycomb import NoOpHoneycomb, honeycomb_span


class HoneycombWrapperTestCase(TestCase):

    def test_uses_noop_when_honeycomb_not_enabled(self):
        with self.settings(USE_HONEYCOMB=False):
            with honeycomb_span('test-span') as context:
                self.assertIsInstance(context, NoOpHoneycomb)

    @mock.patch('beeline.add_context')
    def test_uses_beeline_when_honeycomb_enabled(self, mock_add_context):
        with self.settings(USE_HONEYCOMB=True):
            with honeycomb_span('test-span') as context:
                self.assertIsInstance(context, FunctionType)

    @mock.patch('beeline.add_context')
    def test_excludes_attributes_not_allowlisted(self, mock_add_context):
        with self.settings(USE_HONEYCOMB=True, HONEYCOMB_ALLOWED_COLUMNS=['allowed']):
            with honeycomb_span('test-span') as context:
                context(allowed='hello', blocked='nogo')

        mock_add_context.assert_called_once_with({'allowed': 'hello'})
