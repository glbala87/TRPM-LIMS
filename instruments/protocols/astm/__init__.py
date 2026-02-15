# instruments/protocols/astm/__init__.py

"""
ASTM E1381/E1394 Protocol Implementation

ASTM (American Society for Testing and Materials) protocols are used for
communication between clinical laboratory instruments and computer systems.

Key features:
- E1381: Low-level data link protocol (framing, checksums)
- E1394: High-level record format (patient, order, result records)

Message structure:
- STX (0x02): Start of text
- Frame number: 1-7, cycling
- Data: Record content
- ETX (0x03) or ETB (0x17): End of text/block
- Checksum: 2 ASCII hex characters
- CR LF: Carriage return, line feed

Record types:
- H: Header record
- P: Patient record
- O: Order record
- R: Result record
- C: Comment record
- L: Terminator record
- Q: Query record
"""

from .parser import ASTMParser
from .encoder import ASTMEncoder
from .handlers import ASTMMessageHandler

__all__ = ['ASTMParser', 'ASTMEncoder', 'ASTMMessageHandler']
