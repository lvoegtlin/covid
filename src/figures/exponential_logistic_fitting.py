from scipy.optimize import curve_fit

from src.figures.abstract_figure import AbstractFigure
import numpy as np

from src.utils.config import Constants
from src.utils.functions import logistic, exponential


class ExponentialLogisticFitting(AbstractFigure):
    headers = ['original', 'logistic', 'exponential']

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.logisticr2 = None
        self.ldoubletime = None
        self.ldoubletimeerror = None
        self.expr2 = None
        self.edoubletime = None
        self.edoubletimeerror = None
        y_copy = np.reshape(np.copy(y), (len(y), 1))
        self.graphs = y_copy
        self.headers = ['original']

        try:
            self._fit_curve_logistic()
            self.headers.append('logistic')
        except:
            pass
        try:
            self._fit_curve_exponential()
            self.headers.append('exponential')
        except:
            pass
        self._calculate_figure_key_data()
        self._create_graph_data()

    def _calculate_figure_key_data(self):
        self._calculate_figure_key_data_logistic()
        self._calculate_figure_key_data_exponential()

    def _calculate_figure_key_data_logistic(self):
        if self.lpopt is None:
            return
        self.lerror = np.sqrt(np.diag(self.lpcov))
        # for logistic curve at half maximum, slope = growth rate/2. so doubling time = ln(2) / (growth rate/2)
        self.ldoubletime = np.log(2) / (self.lpopt[1] / 2)
        # standard error
        self.ldoubletimeerror = 1.96 * self.ldoubletime * np.abs(self.lerror[1] / self.lpopt[1])
        # calculate R^2
        residuals = self.y - logistic(self.x, *self.lpopt)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((self.y - np.mean(self.y)) ** 2)
        self.logisticr2 = 1 - (ss_res / ss_tot)

    def _calculate_figure_key_data_exponential(self):
        if self.epcov is None:
            return
        self.eerror = np.sqrt(np.diag(self.epcov))
        # for exponential curve, slope = growth rate. so doubling time = ln(2) / growth rate
        self.edoubletime = np.log(2) / self.epopt[1]
        # standard error
        self.edoubletimeerror = 1.96 * self.edoubletime * np.abs(self.eerror[1] / self.epopt[1])
        # calculate R^2
        residuals = self.y - exponential(self.x, *self.epopt)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((self.y - np.mean(self.y)) ** 2)
        self.expr2 = 1 - (ss_res / ss_tot)

    def _create_graph_data(self):
        if self.logisticr2 > Constants.R2_LIMIT:
            y_logistic = logistic(self.x, *self.lpopt)
            y_logistic = np.reshape(np.copy(y_logistic), (len(y_logistic), 1))
            self.graphs = np.concatenate((self.graphs, y_logistic), axis=1)

        if self.expr2 > Constants.R2_LIMIT:
            y_exponential = exponential(self.x, *self.epopt)
            y_exponential = np.reshape(np.copy(y_exponential), (len(y_exponential), 1))
            self.graphs = np.concatenate((self.graphs, y_exponential), axis=1)

    def _fit_curve_logistic(self):
        self.lpopt, self.lpcov = curve_fit(logistic, self.x, self.y, maxfev=10000)

    def _fit_curve_exponential(self):
        self.epopt, self.epcov = curve_fit(exponential, self.x, self.y, bounds=([0, 0, -100], [100, 0.9, 100]),
                                           maxfev=10000)

    def get_graphs(self):
        return self.graphs.tolist()

    def get_figure_key_data(self):
        return {
            "y_original": self.y,
            "expr2": self.expr2,
            "edoubletime": self.edoubletime,
            "edoubletimeerror": self.edoubletimeerror,
            "logisticr2": self.logisticr2,
            "ldoubletime": self.ldoubletime,
            "ldoubletimeerror": self.ldoubletimeerror
        }
