import os
import signal
import subprocess

import configargparse
from django.core.management.base import BaseCommand, CommandError, DjangoHelpFormatter


class CommandParser(configargparse.ArgParser):
    """
    Customized ArgumentParser class to improve some error messages and prevent
    SystemExit in several occasions, as SystemExit is unacceptable when a
    command is called programmatically.

    Currently its unclear why the linter has issues with `error()`,
    but we disable the few annoying rules
    """
    def __init__(self, *, missing_args_message=None, called_from_command_line=None, **kwargs):
        self.missing_args_message = missing_args_message
        self.called_from_command_line = called_from_command_line
        super().__init__(**kwargs)

    def parse_args(self, args=None, namespace=None):
        # Catch missing argument for a better error message
        if (self.missing_args_message and not (args or any(not arg.startswith('-') for arg in args))):
            self.error(self.missing_args_message)
        return super().parse_args(args, namespace)

    def error(self, message):
        if self.called_from_command_line:
            super().error(message)
        else:
            raise CommandError('Error: %s' % message)


class AdminCommand(BaseCommand):

    help = 'There is no description for this command.'

    DEFAULT_CONFIG_DIRS = ['.commands']

    def add_arguments(self, parser: configargparse.ArgumentParser) -> None:
        """Add arguments to the command
        """

    def create_parser(self, prog_name, subcommand, **kwargs) -> configargparse.ArgumentParser:
        """
        This is a copy of the normal `create_parser` method, but it includes
        the defaults for using the ConfigArgParser argument parser
        https://github.com/django/django/blob/master/django/core/management/base.py#L271
        """
        parser = CommandParser(
            # ConfigArgParser values
            config_file_parser_class=configargparse.YAMLConfigFileParser,
            default_config_files=list(
                # creates a config file at "{DIR}/{COMMAND}.yaml" --> ".commands/track_stack.yaml"
                map(lambda d: os.path.join(d, f'{subcommand}.yaml'), self.DEFAULT_CONFIG_DIRS)
            ),
            # Default Django values
            prog='%s %s' % (os.path.basename(prog_name), subcommand),
            description=getattr(self, 'help', ''),
            formatter_class=DjangoHelpFormatter,
            missing_args_message=getattr(self, 'missing_args_message', None),
            called_from_command_line=getattr(self, '_called_from_command_line', None),
            **kwargs
        )
        parser.add_argument('--version', action='version', version=self.get_version())
        parser.add_argument(
            '-v', '--verbosity', default=1,
            type=int, choices=[0, 1, 2, 3],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output',
        )
        parser.add_argument(
            '--settings',
            help=(
                'The Python path to a settings module, e.g. '
                '"myproject.settings.main". If this isn\'t provided, the '
                'DJANGO_SETTINGS_MODULE environment variable will be used.'
            ),
        )
        parser.add_argument(
            '--pythonpath',
            help='A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".',
        )
        parser.add_argument('--traceback', action='store_true', help='Raise on CommandError exceptions')
        parser.add_argument(
            '--no-color', action='store_true',
            help="Don't colorize the command output.",
        )
        parser.add_argument(
            '--force-color', action='store_true',
            help='Force colorization of the command output.',
        )
        if self.requires_system_checks:
            parser.add_argument(
                '--skip-checks', action='store_true',
                help='Skip system checks.',
            )
        self.add_arguments(parser)
        return parser

    def execute(self, *args, **options):
        try:
            return super().execute(*args, **options)
        except KeyboardInterrupt:
            self.abort('Quit due to Keyboard Interrupt')

    def handle(self, *args, **options):
        self.abort('This command is not implemented.')

    def progress_bar(self, iterable, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd='\r'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        total = len(iterable)

        # Progress Bar Printing Function
        def printProgressBar(iteration):
            percent = ('{0:.' + str(decimals) + 'f}').format(100 * (iteration / float(total)))
            filledLength = int(length * iteration // total)
            percent_bar = fill * filledLength + '-' * (length - filledLength)
            print(f'\r{prefix} |{percent_bar}| {percent}% {suffix}', end=printEnd)
        # Initial Call
        printProgressBar(0)
        # Update Progress Bar
        for i, item in enumerate(iterable):
            yield item
            printProgressBar(i + 1)
        # Print New Line on Complete
        print()

    def subprocess(self, args, acceptable_codes=(0,), raise_on_code=True, **kwargs):
        self.info(f'$> {" ".join(args)}')
        output = []
        try:
            p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, **kwargs)
            for line in iter(p.stdout.readline, b''):
                line_str = line.decode('utf-8')
                self.output(line_str)
                output.append(line_str)

            p.stdout.close()
            p.wait()
        except KeyboardInterrupt:
            p.send_signal(signal.SIGINT)
            p.wait()
        if p.returncode not in acceptable_codes and raise_on_code:
            codes = ', '.join([str(x) for x in acceptable_codes])
            self.abort(f'{args[0]} returned a code that was not in acceptable range [{codes}]')
        return p.returncode, output

    def abort(self, error):
        """Exit the command due to an error
        """
        self.error(error)
        raise CommandError('Aborted')

    def success(self, msg):
        """Print a success message
        """
        self.stdout.write(self.style.SUCCESS(msg))

    def info(self, msg):
        self.stdout.write(self.style.SQL_KEYWORD(msg))

    def output(self, msg):
        self.stdout.write(msg)

    def error(self, msg):
        """Print a error message
        """
        self.stdout.write(self.style.ERROR(msg))
