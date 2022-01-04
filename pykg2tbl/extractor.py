# Use this file to describe the datamodel handled by this module
# we recommend using abstract classes to achieve proper service and interface insulation
from abc import ABC  # , abstractmethod


class MyModel(ABC):
    """
    Documentation should capture what this class is about. Mention mainly its responsibility and collaboration with others classes.
    """

    def __init__(self, p1: str = "whatever"):
        """
        constructor

        :param p1: Documentation should focus on the meaning and constraints of the parameters to the constructor
        """
        pass

    def my_method(self, p2: int = 0) -> float:
        """
        This method will do something described here.
        The text can reference some class :class:`~MyModel` or a specific function :func:`~MyModel.my_method`

        :param p2: argument meaning, purpose, expectations, constraints
        :type p2: int
        :returns: a description of the result
        :rtype: float
        :raises MyException: when something strange happens
        """
        assert 0 < p2 < 100, "parameter out of range"
        return pow(p2/100, 2)
