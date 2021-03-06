from scipy.optimize import curve_fit

from src.figures.abstract_figure import AbstractFigure
import numpy as np

from src.utils.config import Constants
from src.utils.functions import logistic, exponential


class ExponentialLogisticFitting(AbstractFigure):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.logisticr2 = 0
        self.ldoubletime = 0
        self.ldoubletimeerror = 0
        self.expr2 = 0
        self.edoubletime = 0
        self.edoubletimeerror = 0
        y_copy = np.reshape(np.copy(y), (len(y), 1))
        self.graphs = y_copy
        self.headers = ['original']

        self.y_logistic, self.lpopt, self.lpcov = self._fit_curve(logistic, {'maxfev': 10000})

        self.y_expo, self.epopt, self.epcov = self._fit_curve(exponential,
                                                              {'bounds': ([0, 0, -100], [100, 0.9, 100]),
                                                               'maxfev': 10000})

        self._calculate_figure_key_data()
        self._create_graph_data()

    def _calculate_figure_key_data(self):
        self._calculate_figure_key_data_logistic()
        self._calculate_figure_key_data_exponential()

    def _calculate_figure_key_data_logistic(self):
        if self.lpopt is None or self.lpopt.size == 0:
            return
        try:
            self.lerror = np.sqrt(np.diag(self.lpcov))
            # for logistic curve at half maximum, slope = growth rate/2. so doubling time = ln(2) / (growth rate/2)
            self.ldoubletime = np.log(2) / (self.lpopt[1] / 2)
            # standard error
            self.ldoubletimeerror = 1.96 * self.ldoubletime * np.abs(self.lerror[1] / self.lpopt[1])
            # calculate R^2
            residuals = self.y - logistic(self.x, *self.lpopt)
            self.logisticr2 = self._calculate_R2(self.x, self._adopt_graph_size(self.y_logistic), self.lpopt, logistic)
        except:
            pass

    def _calculate_figure_key_data_exponential(self):
        if self.epcov is None or self.epopt.size == 0:
            return
        try:
            self.eerror = np.sqrt(np.diag(self.epcov))
            # for exponential curve, slope = growth rate. so doubling time = ln(2) / growth rate
            self.edoubletime = np.log(2) / self.epopt[1]
            # standard error
            self.edoubletimeerror = 1.96 * self.edoubletime * np.abs(self.eerror[1] / self.epopt[1])
            # calculate R^2
            self.expr2 = self._calculate_R2(self.x, self._adopt_graph_size(self.y_expo), self.epopt, exponential)
        except:
            pass

    def _calculate_R2(self, x, y, points, function):
        residuals = y - function(x, *points)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        if ss_tot == 0:
            return 0
        return 1 - (ss_res / ss_tot)

    def _create_graph_data(self):
        if self.logisticr2 > Constants.R2_LIMIT:
            y_logistic = logistic(self.x, *self.lpopt)
            # if we have a smaller array
            container = self._adopt_graph_size(y_logistic)
            container = np.reshape(np.copy(container), (len(container), 1))
            self.graphs = np.concatenate((self.graphs, container), axis=1)
            self.headers.append('logistic')

        if self.expr2 > Constants.R2_LIMIT:
            y_exponential = exponential(self.x, *self.epopt)
            container = self._adopt_graph_size(y_exponential)
            container = np.reshape(np.copy(container), (len(container), 1))
            self.graphs = np.concatenate((self.graphs, container), axis=1)
            self.headers.append('exponential')

    def _adopt_graph_size(self, y):

        if y.size < self.y.size:
            container = np.arange(self.y.size)
            container[self.y.size - y.size:] = y
        elif y.size > self.y.size:
            container = y[y.size - self.y.size:]
        else:
            container = y
        return container

    def _fit_curve(self, function, parameters):
        # start where the first datapoint is not 0 and then add some 0 and compare the cov
        best_r2 = 0
        best_y = np.asarray([])
        best_opt = np.asarray([])
        best_cov = np.asarray([])
        no_zero_data = self.y[self.y != 0]
        for i in np.arange(no_zero_data.size):
            new_size = no_zero_data.size + i
            new_y = np.zeros(new_size)
            new_y[new_size - no_zero_data.size:] = no_zero_data
            # fitting curve
            try:
                opt, cov = curve_fit(function, self.x, self.y, **parameters)
            except:
                continue
            r2 = self._calculate_R2(np.arange(new_y.size), new_y, opt, function)
            if r2 > best_r2:
                best_r2 = r2
                best_y = new_y
                best_opt = opt
                best_cov = cov

        return best_y, best_opt, best_cov

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
