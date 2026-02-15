# instruments/protocols/hl7/__init__.py

"""
HL7 v2.x Protocol Implementation

Health Level Seven (HL7) is a standard for exchanging information between
medical applications. This implementation supports HL7 v2.x messages
commonly used in laboratory information systems.

Message structure:
- MLLP framing: <VT>message<FS><CR>
- Segments separated by <CR>
- Fields separated by |
- Components separated by ^
- Subcomponents separated by &

Common message types:
- ORM: Order Message (orders from LIS to instrument)
- ORU: Observation Result (results from instrument to LIS)
- QRY: Query Message
- ACK: Acknowledgment Message
- ADT: Admit/Discharge/Transfer

Common segments:
- MSH: Message Header
- PID: Patient Identification
- OBR: Observation Request
- OBX: Observation Result
- ORC: Common Order
"""

from .parser import HL7Parser
from .encoder import HL7Encoder
from .handlers import HL7MessageHandler

__all__ = ['HL7Parser', 'HL7Encoder', 'HL7MessageHandler']
