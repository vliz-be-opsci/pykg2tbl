class MyOwnException(Exception):
    """
    Raised when this happens...
    """

    def __init__(self, cast, message):
        self.message = message
        self.cast = cast
