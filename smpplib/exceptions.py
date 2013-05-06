#
# Exceptions
#


class UnknownCommandError(Exception):
    """Raised when unknown command ID is received"""


class ConnectionError(Exception):
    """Connection error"""


class PDUError(RuntimeError):
    """Error processing PDU"""


class MessageTooLong(ValueError):
    """Text too long to fit 255 SMS"""
