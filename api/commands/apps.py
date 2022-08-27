from os import path

from django.apps import AppConfig
from django.conf import settings
from django.utils.autoreload import autoreload_started


def autoreload_watch(sender, **kwargs):
    """Add any non-Python files to autoreload the server on
    """
    sender.watch_dir(path.dirname(settings.SWAGGER_DESCRIPTION_PATH), '*.md')
    sender.watch_dir(path.dirname(settings.SWAGGER_DESCRIPTION_PATH), '*.yaml')


class CommandsConfig(AppConfig):
    name = f'{settings.API_IMPORT_ROOT}.commands'
    default = True

    def ready(self):
        autoreload_started.connect(autoreload_watch)
