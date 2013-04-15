#
# Exceptions
#

class UnknownCommandError(Exception):
    """Raised when unknown command ID is received"""

class ConnectionError(Exception):
    """Connection error"""

class PDUError(RuntimeError):
    """Error processing PDU"""

