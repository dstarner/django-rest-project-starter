import socket
import time

from django.conf import settings

from ..base import AdminCommand


class Command(AdminCommand):
    """
    Tries to make a connection to the database
    This is used by Docker to ensure the database is up and running
    """
    requires_system_checks = ()

    DEFAULT_MAX_TRIES = 4
    DEFAULT_DELAY = 4
    DATABASE_SETTINGS = settings.DATABASES['default']

    connected = False

    def add_arguments(self, parser):
        parser.add_argument('--host', type=str, default=self.DATABASE_SETTINGS['HOST'])
        parser.add_argument('--port', type=int, default=int(self.DATABASE_SETTINGS['PORT']))
        parser.add_argument(
            '-t',
            '--max-tries',
            dest='max_tries',
            default=self.DEFAULT_MAX_TRIES,
            type=int,
            help='Number of connection attempts to make before failing'
        )
        parser.add_argument(
            '-d',
            '--delay',
            dest='delay',
            default=self.DEFAULT_DELAY,
            help='Delay in seconds between each failed connection'
        )

    def _successful_connection(self, host, port, sock=None):
        """Attempt to connect to the default database
        """
        if not sock:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connected = sock.connect_ex((host, int(port))) == 0
        except socket.gaierror as exc:
            self.info(f'{str(exc)}: {host}:{port}')
            self.connected = False
        return self.connected

    def handle(self, *args, **options):
        """Attempt a certain number of connections and sleep between them
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        max_tries = options.get('max_tries', self.DEFAULT_MAX_TRIES)
        delay = options.get('delay', self.DEFAULT_DELAY)

        tries = 0

        while tries <= max_tries and not self._successful_connection(options['host'], options['port'], sock):
            tries += 1
            # No point in sleeping if we are just exiting
            if tries <= max_tries:
                self.info(
                    '[%d/%d] Could not connect to the database...Trying again in %d seconds' % (tries, max_tries, delay)
                )
                time.sleep(delay)

        if self.connected:
            self.success('Connected to the database')
        else:
            self.abort('Could not connect to the database')
