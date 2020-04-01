from abc import abstractmethod, ABCMeta


class SafeSingleton(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AbstractFigure(SafeSingleton):

    @abstractmethod
    def get_figure_key_data(self):
        pass

    @abstractmethod
    def get_graphs(self):
        pass
