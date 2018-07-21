from abc import abstractmethod, ABC
from typing import Union
from ..Tools.Hash import HashCalculator
from ..Magic.Classic import discrete_cache


class IData:
    __structure__: object
    __sig_str__: object  # object(s) for showing.

    def __destruct__(self):
        raise NotImplemented


class Hash(ABC):

    @abstractmethod
    def __hash__(self):
        raise NotImplemented


class Eq(ABC):

    @abstractmethod
    def __eq__(self, other):
        raise NotImplemented


class Ord(Eq, ABC):  # ordered

    @abstractmethod
    def __lt__(self, other):
        raise NotImplemented


class Ind(ABC):

    @abstractmethod
    def __getitem__(self, item):
        raise NotImplemented


class Dense(Eq):
    def __eq__(self: IData, other):
        # noinspection PyUnresolvedReferences

        return isinstance(other, Dense) and (
            self.__structure__ == other.__structure__ if self.__structure__ else self is other)


class Im(Hash):  # Immutable

    @discrete_cache
    def _hash_cache(self):
        collector = HashCalculator()
        collector.take(self.__class__)
        return collector

    def __hash__(self: 'Union[Im, IData]'):
        return self._hash_cache().extensive_collect(1, (self.__structure__,))


class ConsInd(Ind):  # index following constructing
    def __getitem__(self: IData, i):
        # noinspection PyUnresolvedReferences
        return self.__structure__[i]


class Discrete(Eq, Im):
    # discrete data is very powerful when using it for imitating Natural Numbers.
    def __eq__(self: IData, other):
        return self is other

    @discrete_cache
    def _hash_cache(self):
        collector = HashCalculator()
        collector.take(id(self), id(Discrete))
        return collector

    @discrete_cache
    def __hash__(self):
        collector = self._hash_cache()
        return collector.extensive_collect(1, (id(self),))
