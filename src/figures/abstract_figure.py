from abc import abstractmethod


class AbstractFigure:

    headers = []

    @abstractmethod
    def get_figure_key_data(self):
        pass

    @abstractmethod
    def get_graphs(self):
        pass
