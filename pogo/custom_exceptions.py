class GeneralPogoException(Exception):
    """Throw an exception that moves up to the start, and reboots"""


class PogoServerException(GeneralPogoException):
    """Raised from suspected error Serverside"""


class PogoResponseException(GeneralPogoException):
    """Throw an exception at bad responses"""


class PogoInventoryException(GeneralPogoException):
    """Uninitialized Inventory"""


class PogoRateException(GeneralPogoException):
    """Requests made too quickly"""
