from django.apps import apps
from django.conf import settings
from django.core.management.commands import makemigrations

from ..base import AdminCommand


class Command(makemigrations.Command, AdminCommand):
    """Overrides the normal makemigrations command to include more validations
    """

    def handle(self, *args, **options):
        errors = {}

        def _uppercase(v, model):
            return v[0].isupper()  # easy way to see if it was overridden

        req_meta_fields = sorted([
            (
                'db_table',
                lambda v, m: v != f'{m._meta.app_label}_{m._meta.model_name}',
                '"%s" must be set explicitly'
            ),
            (
                'default_related_name', lambda v, m: v is not None, '"%s" must be set explicitly'
            ),
            (
                'ordering', lambda v, m: v, '"%s" must be set explicitly'
            ),
            (
                'verbose_name', _uppercase, '"%s" must be set and capitalized'
            ),
            (
                'verbose_name_plural', _uppercase, '"%s" must be set and capitalized'
            ),
        ], key=lambda v: v[0])
        for _, config in apps.app_configs.items():
            if not config.name.startswith(settings.API_IMPORT_ROOT):
                continue
            models = config.get_models()
            for model in models:
                local_errors = []
                for field, validate, err_msg in req_meta_fields:
                    if not validate(getattr(model._meta, field), model):
                        local_errors.append(err_msg % field)

                if local_errors:
                    errors[f'{model._meta.verbose_name} ({config.name})'] = local_errors

        if errors:
            nl = '\n'
            err_str = '\n\n'.join([
                f'{model}:{nl}  - {f"{nl}  - ".join(errs)}'
                for model, errs in errors.items()
            ])
            self.abort(f'-- Model Validation Failed --\n\n{err_str}{nl}')
        self.success('All model Metas were successfully validated')
        super().handle(*args, **options)
