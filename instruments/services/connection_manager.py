# instruments/services/connection_manager.py

"""
Connection Manager Service

Manages TCP/Serial connections to laboratory instruments.
"""

import logging
import socket
import threading
import time
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager

from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class ActiveConnection:
    """Represents an active instrument connection."""
    connection_id: int
    conn_socket: Optional['socket.socket'] = None
    thread: Optional[threading.Thread] = None
    running: bool = False
    last_activity: datetime = None
    error_count: int = 0

    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = datetime.now()


class ConnectionManager:
    """
    Manages connections to laboratory instruments.

    This service handles:
    - Starting and stopping TCP server/client connections
    - Managing connection lifecycle
    - Routing received messages to appropriate handlers
    - Sending messages to instruments
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern to ensure one connection manager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.connections: Dict[int, ActiveConnection] = {}
        self.handlers: Dict[int, Any] = {}
        self._shutdown = False
        self._manager_lock = threading.Lock()

    def start_connection(self, connection) -> bool:
        """
        Start a connection to an instrument.

        Args:
            connection: InstrumentConnection model instance

        Returns:
            bool: True if connection started successfully
        """
        from ..models import InstrumentConnection

        connection_id = connection.pk

        with self._manager_lock:
            if connection_id in self.connections:
                if self.connections[connection_id].running:
                    logger.warning(f"Connection {connection_id} is already running")
                    return True

        try:
            # Create protocol handler
            handler = self._create_handler(connection)
            self.handlers[connection_id] = handler

            # Start connection based on type
            if connection.connection_type == 'TCP_SERVER':
                return self._start_tcp_server(connection, handler)
            elif connection.connection_type == 'TCP_CLIENT':
                return self._start_tcp_client(connection, handler)
            elif connection.connection_type == 'SERIAL':
                return self._start_serial(connection, handler)
            else:
                logger.error(f"Unknown connection type: {connection.connection_type}")
                return False

        except Exception as e:
            logger.exception(f"Error starting connection {connection_id}: {e}")
            connection.update_connection_status('ERROR', str(e))
            return False

    def stop_connection(self, connection) -> bool:
        """
        Stop a connection to an instrument.

        Args:
            connection: InstrumentConnection model instance

        Returns:
            bool: True if connection stopped successfully
        """
        connection_id = connection.pk

        with self._manager_lock:
            if connection_id not in self.connections:
                logger.warning(f"Connection {connection_id} not found")
                return True

            active = self.connections[connection_id]
            active.running = False

            # Close socket
            if active.conn_socket:
                try:
                    active.conn_socket.close()
                except Exception as e:
                    logger.warning(f"Error closing socket: {e}")

            # Wait for thread to finish
            if active.thread and active.thread.is_alive():
                active.thread.join(timeout=5.0)

            # Remove from active connections
            del self.connections[connection_id]

            # Remove handler
            if connection_id in self.handlers:
                del self.handlers[connection_id]

        # Update status
        connection.update_connection_status('DISCONNECTED')
        logger.info(f"Connection {connection_id} stopped")
        return True

    def test_connection(self, connection) -> Dict[str, Any]:
        """
        Test a connection to an instrument.

        Args:
            connection: InstrumentConnection model instance

        Returns:
            dict: Test results with 'success', 'response_time', 'error' keys
        """
        start_time = time.time()

        try:
            if connection.connection_type in ('TCP_SERVER', 'TCP_CLIENT'):
                # Test TCP connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(connection.timeout)

                try:
                    if connection.connection_type == 'TCP_CLIENT':
                        sock.connect((connection.host, connection.port))
                    else:
                        # For server mode, just verify we can bind
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        sock.bind((connection.host, connection.port))

                    response_time = int((time.time() - start_time) * 1000)

                    return {
                        'success': True,
                        'response_time': response_time,
                        'message': 'Connection test successful'
                    }
                finally:
                    sock.close()

            elif connection.connection_type == 'SERIAL':
                # Test serial port availability
                try:
                    import serial
                    ser = serial.Serial(
                        port=connection.serial_port,
                        baudrate=connection.baud_rate,
                        timeout=connection.timeout
                    )
                    ser.close()

                    response_time = int((time.time() - start_time) * 1000)

                    return {
                        'success': True,
                        'response_time': response_time,
                        'message': 'Serial port available'
                    }
                except ImportError:
                    return {
                        'success': False,
                        'error': 'pyserial not installed'
                    }

        except socket.timeout:
            return {
                'success': False,
                'error': 'Connection timed out'
            }
        except ConnectionRefusedError:
            return {
                'success': False,
                'error': 'Connection refused'
            }
        except socket.error as e:
            return {
                'success': False,
                'error': f'Socket error: {e}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def send_message(self, connection, message: bytes) -> Dict[str, Any]:
        """
        Send a message to an instrument.

        Args:
            connection: InstrumentConnection model instance
            message: Bytes to send

        Returns:
            dict: Result with 'success' and 'error' keys
        """
        connection_id = connection.pk

        with self._manager_lock:
            if connection_id not in self.connections:
                return {
                    'success': False,
                    'error': 'Connection not active'
                }

            active = self.connections[connection_id]
            if not active.running or not active.conn_socket:
                return {
                    'success': False,
                    'error': 'Connection not running'
                }

            try:
                active.conn_socket.sendall(message)
                active.last_activity = datetime.now()
                connection.update_last_message()

                # Log the message
                self._log_message(connection, 'OUTBOUND', message)

                return {
                    'success': True,
                    'bytes_sent': len(message)
                }

            except Exception as e:
                logger.error(f"Error sending message: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

    def get_connection_status(self, connection) -> Dict[str, Any]:
        """Get the current status of a connection."""
        connection_id = connection.pk

        with self._manager_lock:
            if connection_id not in self.connections:
                return {
                    'running': False,
                    'status': 'DISCONNECTED'
                }

            active = self.connections[connection_id]
            return {
                'running': active.running,
                'status': 'CONNECTED' if active.running else 'DISCONNECTED',
                'last_activity': active.last_activity.isoformat() if active.last_activity else None,
                'error_count': active.error_count
            }

    def _create_handler(self, connection):
        """Create the appropriate protocol handler."""
        from ..protocols.astm.handlers import ASTMMessageHandler
        from ..protocols.hl7.handlers import HL7MessageHandler

        def on_message_received(message):
            self._handle_received_message(connection, message)

        def on_error(error):
            logger.error(f"Protocol error on connection {connection.pk}: {error}")

        if connection.protocol == 'ASTM':
            return ASTMMessageHandler(
                on_message_received=on_message_received,
                on_error=on_error
            )
        elif connection.protocol == 'HL7':
            return HL7MessageHandler(
                on_message_received=on_message_received,
                on_error=on_error,
                sending_application='LIMS',
                auto_acknowledge=True
            )
        else:
            # Custom protocol - return a basic handler
            return None

    def _start_tcp_server(self, connection, handler) -> bool:
        """Start a TCP server for incoming connections."""
        connection_id = connection.pk

        def server_thread():
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                server_socket.bind((connection.host, connection.port))
                server_socket.listen(1)
                server_socket.settimeout(1.0)  # Allow periodic checks

                connection.update_connection_status('CONNECTED')
                logger.info(f"TCP server listening on {connection.host}:{connection.port}")

                active = self.connections.get(connection_id)
                if not active:
                    return

                while active.running:
                    try:
                        client_socket, client_addr = server_socket.accept()
                        logger.info(f"Client connected from {client_addr}")

                        # Handle client in same thread for simplicity
                        self._handle_client(connection, client_socket, handler)

                    except socket.timeout:
                        continue
                    except Exception as e:
                        if active.running:
                            logger.error(f"Server error: {e}")
                            active.error_count += 1

            except Exception as e:
                logger.error(f"Failed to start server: {e}")
                connection.update_connection_status('ERROR', str(e))
            finally:
                server_socket.close()
                connection.update_connection_status('DISCONNECTED')

        # Create and start thread
        active = ActiveConnection(
            connection_id=connection_id,
            running=True
        )

        thread = threading.Thread(
            target=server_thread,
            name=f"InstrumentServer-{connection_id}",
            daemon=True
        )

        active.thread = thread
        self.connections[connection_id] = active

        thread.start()
        return True

    def _start_tcp_client(self, connection, handler) -> bool:
        """Start a TCP client connection."""
        connection_id = connection.pk

        def client_thread():
            active = self.connections.get(connection_id)
            if not active:
                return

            retry_count = 0

            while active.running and retry_count <= connection.max_retries:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(connection.timeout)
                    sock.connect((connection.host, connection.port))

                    active.conn_socket = sock
                    connection.update_connection_status('CONNECTED')
                    logger.info(f"Connected to {connection.host}:{connection.port}")

                    retry_count = 0  # Reset on successful connection

                    # Handle communication
                    self._handle_client(connection, sock, handler)

                except socket.timeout:
                    logger.warning(f"Connection timeout to {connection.host}:{connection.port}")
                    retry_count += 1
                except ConnectionRefusedError:
                    logger.warning(f"Connection refused by {connection.host}:{connection.port}")
                    retry_count += 1
                except Exception as e:
                    logger.error(f"Client error: {e}")
                    retry_count += 1
                    active.error_count += 1

                if active.running and retry_count <= connection.max_retries:
                    connection.update_connection_status('CONNECTING')
                    time.sleep(connection.retry_interval)

            if retry_count > connection.max_retries:
                connection.update_connection_status('ERROR', 'Max retries exceeded')

            connection.update_connection_status('DISCONNECTED')

        # Create and start thread
        active = ActiveConnection(
            connection_id=connection_id,
            running=True
        )

        thread = threading.Thread(
            target=client_thread,
            name=f"InstrumentClient-{connection_id}",
            daemon=True
        )

        active.thread = thread
        self.connections[connection_id] = active

        connection.update_connection_status('CONNECTING')
        thread.start()
        return True

    def _start_serial(self, connection, handler) -> bool:
        """Start a serial port connection."""
        try:
            import serial
        except ImportError:
            logger.error("pyserial not installed")
            connection.update_connection_status('ERROR', 'pyserial not installed')
            return False

        connection_id = connection.pk

        def serial_thread():
            active = self.connections.get(connection_id)
            if not active:
                return

            try:
                ser = serial.Serial(
                    port=connection.serial_port,
                    baudrate=connection.baud_rate,
                    timeout=1.0
                )

                connection.update_connection_status('CONNECTED')
                logger.info(f"Serial port {connection.serial_port} opened")

                while active.running:
                    try:
                        if ser.in_waiting > 0:
                            data = ser.read(ser.in_waiting)
                            if data:
                                active.last_activity = datetime.now()
                                connection.update_last_message()

                                # Log and process message
                                self._log_message(connection, 'INBOUND', data)

                                if handler:
                                    response = handler.handle_received_data(data)
                                    if response:
                                        ser.write(response)
                                        self._log_message(connection, 'OUTBOUND', response)

                        time.sleep(0.1)

                    except Exception as e:
                        logger.error(f"Serial read error: {e}")
                        active.error_count += 1

            except Exception as e:
                logger.error(f"Failed to open serial port: {e}")
                connection.update_connection_status('ERROR', str(e))
            finally:
                if 'ser' in locals():
                    ser.close()
                connection.update_connection_status('DISCONNECTED')

        # Create and start thread
        active = ActiveConnection(
            connection_id=connection_id,
            running=True
        )

        thread = threading.Thread(
            target=serial_thread,
            name=f"InstrumentSerial-{connection_id}",
            daemon=True
        )

        active.thread = thread
        self.connections[connection_id] = active

        thread.start()
        return True

    def _handle_client(self, connection, client_socket, handler):
        """Handle communication with a connected client."""
        connection_id = connection.pk
        active = self.connections.get(connection_id)

        if not active:
            client_socket.close()
            return

        active.conn_socket = client_socket
        client_socket.settimeout(1.0)

        try:
            while active.running:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break

                    active.last_activity = datetime.now()
                    connection.update_last_message()

                    # Log inbound message
                    self._log_message(connection, 'INBOUND', data)

                    # Process with handler
                    if handler:
                        response = handler.handle_received_data(data)
                        if response:
                            client_socket.sendall(response)
                            self._log_message(connection, 'OUTBOUND', response)

                except socket.timeout:
                    continue
                except Exception as e:
                    if active.running:
                        logger.error(f"Client communication error: {e}")
                        active.error_count += 1
                    break

        finally:
            client_socket.close()
            active.conn_socket = None

    def _handle_received_message(self, connection, message):
        """Handle a fully parsed message from the protocol handler."""
        from .result_importer import ResultImporter

        try:
            importer = ResultImporter()
            importer.import_from_message(connection, message)
        except Exception as e:
            logger.error(f"Error importing message: {e}")

    def _log_message(self, connection, direction: str, data: bytes):
        """Log a message to the database."""
        from ..models import MessageLog

        try:
            raw_message = data.decode('latin-1', errors='replace')

            # Determine message type based on protocol and content
            message_type = self._determine_message_type(connection.protocol, raw_message)

            MessageLog.objects.create(
                connection=connection,
                direction=direction,
                message_type=message_type,
                raw_message=raw_message,
                status='RECEIVED' if direction == 'INBOUND' else 'SENT'
            )
        except Exception as e:
            logger.error(f"Error logging message: {e}")

    def _determine_message_type(self, protocol: str, raw_message: str) -> str:
        """Determine the message type based on protocol and content."""
        if protocol == 'ASTM':
            if raw_message.startswith('H') or '\x02' in raw_message and 'H|' in raw_message:
                return 'ASTM_HEADER'
            elif 'R|' in raw_message:
                return 'ASTM_RESULT'
            elif 'O|' in raw_message:
                return 'ASTM_ORDER'
            elif 'P|' in raw_message:
                return 'ASTM_PATIENT'
            elif 'Q|' in raw_message:
                return 'ASTM_QUERY'
            elif 'L|' in raw_message:
                return 'ASTM_TERMINATOR'

        elif protocol == 'HL7':
            if 'MSH|' in raw_message:
                if 'ORU' in raw_message:
                    return 'HL7_ORU'
                elif 'ORM' in raw_message:
                    return 'HL7_ORM'
                elif 'ACK' in raw_message:
                    return 'HL7_ACK'
                elif 'QRY' in raw_message or 'QBP' in raw_message:
                    return 'HL7_QRY'
                elif 'ADT' in raw_message:
                    return 'HL7_ADT'

        return 'UNKNOWN'

    def shutdown(self):
        """Shutdown all connections."""
        self._shutdown = True

        with self._manager_lock:
            for connection_id in list(self.connections.keys()):
                active = self.connections[connection_id]
                active.running = False

                if active.conn_socket:
                    try:
                        active.conn_socket.close()
                    except Exception:
                        pass

            # Wait for threads to finish
            for connection_id, active in self.connections.items():
                if active.thread and active.thread.is_alive():
                    active.thread.join(timeout=5.0)

            self.connections.clear()
            self.handlers.clear()

        logger.info("Connection manager shutdown complete")
