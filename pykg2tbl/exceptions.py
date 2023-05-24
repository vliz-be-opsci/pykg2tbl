class WrongInputFormat(Exception):
    """Raised when this happens..."""

    def __init__(self, message):
        message = "Wrong input format. QueryResult only allow for List[dicts]"
        super().__init__(message)
