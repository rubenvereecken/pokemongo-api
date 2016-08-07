class GeneralPogoException(Exception):
    """Throw an exception that moves up to the start, and reboots"""


class PogoResponseException(GeneralPogoException):
    """Throw an exception at bad responses"""
