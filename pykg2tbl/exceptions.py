class WrongInputFormat(Exception):
    """Raised when the input is not in a valid format"""

    def __init__(
        self, input_format="Iterable[dicts]", class_failed="QueryResult"
    ):
        message = (
            f"Wrong input format. {class_failed} "
            f"only allows for {input_format}"
        )
        super().__init__(message)


class MultipleSourceTypes(Exception):
    """Raised when the input has multiple source type"""

    def __init__(self):
        message = (
            "The input has multiple file sources. "
            "The current implementation only allows "
            "for one file source per object."
        )
        super().__init__(message)


class NoGraphSource(Exception):
    """Raised when the input in KGGraph is not a graph"""

    def __init__(self):
        message = "The input needs to be a graph object."
        super().__init__(message)


class NotASubClass(Exception):
    """Raised when class is not a subclass of Given Parent Class"""

    def __init__(self, parent_class="QueryResult"):
        message = (
            "The class you are trying to register "
            f"is not a subclass of {parent_class}."
        )
        super().__init__(message)


class NoCompatibilityChecker(Exception):
    """Raised when class does not have the compatible checker"""

    def __init__(self):
        message = (
            "The registered class does not have a check_compatibility method"
        )
        super().__init__(message)


class CompatibilityCheckerNotCallable(Exception):
    """Raised when the compatible checker is not a callable"""

    def __init__(self):
        message = (
            "The check_compatibility method in the "
            "registered class is not a callable"
        )
        super().__init__(message)
