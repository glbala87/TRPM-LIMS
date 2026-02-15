# instruments/management/commands/instrument_listener.py

"""
Django management command for running the instrument listener service.

This command starts the connection manager and listens for instrument connections.
It handles graceful shutdown on SIGTERM/SIGINT.
"""

import signal
import time
import sys
import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start the instrument listener service to receive data from laboratory instruments'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        self.manager = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--connection',
            '-c',
            type=int,
            help='Specific connection ID to start (default: all active connections)',
        )
        parser.add_argument(
            '--daemon',
            '-d',
            action='store_true',
            help='Run as a daemon (suppress stdout logging)',
        )
        parser.add_argument(
            '--poll-interval',
            type=int,
            default=5,
            help='Status check interval in seconds (default: 5)',
        )
        parser.add_argument(
            '--no-auto-reconnect',
            action='store_true',
            help='Disable automatic reconnection on failure',
        )

    def handle(self, *args, **options):
        from instruments.models import InstrumentConnection
        from instruments.services.connection_manager import ConnectionManager

        connection_id = options.get('connection')
        daemon_mode = options.get('daemon')
        poll_interval = options.get('poll_interval')
        auto_reconnect = not options.get('no_auto_reconnect')

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        # Configure logging
        if daemon_mode:
            logging.basicConfig(level=logging.WARNING)
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            )

        self.stdout.write(self.style.SUCCESS('Starting instrument listener service...'))

        try:
            # Get connection manager instance
            self.manager = ConnectionManager()

            # Get connections to start
            if connection_id:
                connections = InstrumentConnection.objects.filter(
                    pk=connection_id,
                    is_active=True
                )
                if not connections.exists():
                    raise CommandError(f'Connection {connection_id} not found or not active')
            else:
                connections = InstrumentConnection.objects.filter(
                    is_active=True,
                    auto_start=True
                )

            if not connections.exists():
                self.stdout.write(self.style.WARNING('No active connections configured'))
                return

            # Start all connections
            started_count = 0
            for connection in connections:
                self.stdout.write(f'Starting connection: {connection.name} ({connection.instrument.name})')
                try:
                    if self.manager.start_connection(connection):
                        started_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'  - Started on {connection.host}:{connection.port} ({connection.get_protocol_display()})'
                        ))
                    else:
                        self.stdout.write(self.style.ERROR(f'  - Failed to start'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  - Error: {e}'))

            if started_count == 0:
                raise CommandError('Failed to start any connections')

            self.stdout.write(self.style.SUCCESS(
                f'\nInstrument listener running with {started_count} connection(s)'
            ))
            self.stdout.write('Press Ctrl+C to stop...\n')

            # Main loop
            while self.running:
                try:
                    time.sleep(poll_interval)

                    # Check connection status and reconnect if needed
                    if auto_reconnect:
                        self._check_and_reconnect(connections)

                    # Log status periodically
                    if not daemon_mode:
                        self._log_status()

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f'Error in main loop: {e}')

        except Exception as e:
            logger.exception(f'Fatal error: {e}')
            raise CommandError(str(e))

        finally:
            self._shutdown()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.stdout.write('\nReceived shutdown signal...')
        self.running = False

    def _check_and_reconnect(self, connections):
        """Check connection status and reconnect failed connections."""
        for connection in connections:
            status = self.manager.get_connection_status(connection)

            if not status['running'] and connection.is_active:
                logger.info(f'Attempting to reconnect: {connection.name}')
                try:
                    self.manager.start_connection(connection)
                except Exception as e:
                    logger.error(f'Reconnection failed: {e}')

    def _log_status(self):
        """Log current connection status."""
        from instruments.models import InstrumentConnection

        connections = InstrumentConnection.objects.filter(is_active=True)

        for connection in connections:
            status = self.manager.get_connection_status(connection)
            status_str = 'CONNECTED' if status['running'] else 'DISCONNECTED'

            if status.get('error_count', 0) > 0:
                logger.warning(
                    f'{connection.name}: {status_str} (errors: {status["error_count"]})'
                )

    def _shutdown(self):
        """Gracefully shutdown all connections."""
        self.stdout.write('Shutting down instrument listener...')

        if self.manager:
            self.manager.shutdown()

        self.stdout.write(self.style.SUCCESS('Instrument listener stopped'))


class InstrumentListenerDaemon:
    """
    Daemon wrapper for the instrument listener.

    This can be used to run the listener as a system service.
    """

    def __init__(self, pidfile='/var/run/instrument_listener.pid'):
        self.pidfile = pidfile
        self.running = False

    def start(self):
        """Start the daemon."""
        import os
        from django.core.management import call_command

        # Check if already running
        if os.path.exists(self.pidfile):
            with open(self.pidfile, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)
                print(f'Daemon already running with PID {pid}')
                return
            except OSError:
                # PID file exists but process not running
                os.remove(self.pidfile)

        # Fork and create daemon process
        pid = os.fork()
        if pid > 0:
            # Parent process
            print(f'Daemon started with PID {pid}')
            return

        # Child process - become session leader
        os.setsid()

        # Fork again to prevent zombie processes
        pid = os.fork()
        if pid > 0:
            os._exit(0)

        # Write PID file
        with open(self.pidfile, 'w') as f:
            f.write(str(os.getpid()))

        # Redirect standard file descriptors
        sys.stdin.close()
        sys.stdout = open('/var/log/instrument_listener.log', 'a')
        sys.stderr = sys.stdout

        # Run the command
        self.running = True
        call_command('instrument_listener', daemon=True)

    def stop(self):
        """Stop the daemon."""
        import os

        if not os.path.exists(self.pidfile):
            print('Daemon not running')
            return

        with open(self.pidfile, 'r') as f:
            pid = int(f.read().strip())

        try:
            os.kill(pid, signal.SIGTERM)
            print(f'Sent SIGTERM to PID {pid}')

            # Wait for process to terminate
            for _ in range(30):
                try:
                    os.kill(pid, 0)
                    time.sleep(1)
                except OSError:
                    break

            # Force kill if still running
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
                print(f'Sent SIGKILL to PID {pid}')
            except OSError:
                pass

        except OSError as e:
            print(f'Error stopping daemon: {e}')

        finally:
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)

    def status(self):
        """Check daemon status."""
        import os

        if not os.path.exists(self.pidfile):
            print('Daemon not running')
            return False

        with open(self.pidfile, 'r') as f:
            pid = int(f.read().strip())

        try:
            os.kill(pid, 0)
            print(f'Daemon running with PID {pid}')
            return True
        except OSError:
            print('Daemon not running (stale PID file)')
            return False
