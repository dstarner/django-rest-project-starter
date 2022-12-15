import sys

from django.conf import settings

from ..base import AdminCommand


class Command(AdminCommand):
    """
    Tries to make a connection to the database
    This is used by Docker to ensure the database is up and running
    """
    requires_system_checks = ()
    help = 'Run flake8 against the application to check for syntax and style errors.'

    ISORT_FIX_ARG = '--fix'

    def add_arguments(self, parser):
        parser.add_argument('--syntax', action='store_true')
        parser.add_argument('--allowed', type=int, default=0)
        parser.add_argument(self.ISORT_FIX_ARG, action='store_true', help='isort will attempt to fix what it can')
        parser.add_argument('--diff', action='store_true', help='same as isort --diff flag')

    def handle(self, *args, **options):

        if not options['syntax']:
            isort_args = [settings.API_IMPORT_ROOT]
            if options['diff']:
                isort_args = ['--diff'] + isort_args
            if not options['fix']:
                isort_args = ['--check-only'] + isort_args
            isort_args = ['isort'] + isort_args
            code, result = self.subprocess(isort_args, raise_on_code=False)
            if code != 0:
                self.abort(
                    'isort returned a non-zero exit code, please fix imports by running '
                    f'"{" ".join(sys.argv)} {self.ISORT_FIX_ARG}"'
                )

        flake_args = ['flake8', settings.API_IMPORT_ROOT, '--statistics', '--count']
        if options['syntax']:
            self.info('Syntax checking...')
            flake_args += ['--select=E9,F63,F7,F82', '--show-source']
        else:
            self.info('Style checking...')
            flake_args += ['--exit-zero', '--max-complexity=10']
        code, result = self.subprocess(flake_args)
        try:
            num_bad = int(result[-1])
        except ValueError as e:
            self.abort(f'Could not parse out flake8 count: {e}')
        allowed = options['allowed']
        if num_bad > allowed:
            self.abort(f'flake8 returned {num_bad} (needs less than or equal to {allowed})')
        else:
            self.success(f'flake8 identified {num_bad} problem(s), which is <= the {allowed} allowed')
