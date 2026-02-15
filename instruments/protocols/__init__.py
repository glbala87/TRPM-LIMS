# instruments/protocols/__init__.py

from .astm.parser import ASTMParser
from .astm.encoder import ASTMEncoder
from .hl7.parser import HL7Parser
from .hl7.encoder import HL7Encoder


def get_parser(protocol):
    """Get the appropriate parser for the protocol."""
    parsers = {
        'ASTM': ASTMParser,
        'HL7': HL7Parser,
    }
    return parsers.get(protocol)


def get_encoder(protocol):
    """Get the appropriate encoder for the protocol."""
    encoders = {
        'ASTM': ASTMEncoder,
        'HL7': HL7Encoder,
    }
    return encoders.get(protocol)
