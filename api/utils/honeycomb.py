import logging
from contextlib import contextmanager
from unittest.mock import Mock

import beeline
from django.conf import settings

logger = logging.getLogger(__name__)


@contextmanager
def honeycomb_span(name, **kwargs):
    """
    Works the same as beeline.tracer, but wraps it conditionally if Honeycomb is not being used.
    It also returns the `add_context` function to easily add more information
    """
    allowed_columns = settings.HONEYCOMB_ALLOWED_COLUMNS

    if not settings.USE_HONEYCOMB:
        yield Mock()
    else:
        with beeline.tracer(name, **kwargs):
            def _add_context(data: dict):
                """This provides a chance to whitelist / filter context columns
                """
                cleaned_data = {k: v for k, v in data.items() if k in allowed_columns}
                if len(cleaned_data) != len(data):
                    logger.warning(
                        '"honeycomb_span" was given context columns not whitelisted: %s',
                        set(data.keys()) - set(cleaned_data.keys())
                    )
                return beeline.add_context(cleaned_data)
            yield _add_context  # return beeline so it can added to
