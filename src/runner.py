import pandas as pd
import numpy as np

from scipy.optimize import curve_fit

from src.report.report import GeneralReport
from src.utils.functions import logistic, exponential
from src.utils.io import create_json

df = pd.read_csv(
    'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
relevance = 0.05
R2_limit = 0.5


def plotCases(dataframe, column, c):
    country, inhabitants = c
    border = int(relevance * (inhabitants / 10000))

    if country is None:
        co = dataframe.iloc[:, 4:].T.sum(axis=1)
        country = 'WorldWide'
    elif country == 'Switzerland':
        co = pd.read_csv(
            'https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/covid19_cases_switzerland_openzh.csv').iloc[
             :, -1]
    else:
        co = dataframe[dataframe[column] == country].iloc[:, 4:].T.sum(axis=1)
    # filter that all data is > {relevance} infection per 10k
    co = co[co >= border]
    co = pd.DataFrame(co)
    co.columns = ['Cases']
    co = co.loc[co['Cases'] > 0]

    y_original = np.array(co['Cases'])
    x_original = np.arange(y_original.size)

    # TODO to switch to actual dates
    # dates = [str(date.today() - timedelta(days=int(i)+1)) for i in np.arange(y_original.size)]
    # dates.reverse()
    dates = np.arange(y_original.size)

    graphs = np.reshape(dates, (len(dates), 1))
    y_copy = np.reshape(np.copy(y_original), (len(y_original), 1))
    graphs = np.concatenate((graphs, y_copy), axis=1)

    logisticr2 = None
    ldoubletime = None
    ldoubletimeerror = None
    try:
        lpopt, lpcov = curve_fit(logistic, x_original, y_original, maxfev=10000)
        lerror = np.sqrt(np.diag(lpcov))

        # for logistic curve at half maximum, slope = growth rate/2. so doubling time = ln(2) / (growth rate/2)
        ldoubletime = np.log(2) / (lpopt[1] / 2)
        # standard error
        ldoubletimeerror = 1.96 * ldoubletime * np.abs(lerror[1] / lpopt[1])

        # calculate R^2
        residuals = y_original - logistic(x_original, *lpopt)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y_original - np.mean(y_original)) ** 2)
        logisticr2 = 1 - (ss_res / ss_tot)

        if logisticr2 > R2_limit:
            y_logistic = logistic(x_original, *lpopt)
            y_logistic = np.reshape(np.copy(y_logistic), (len(y_logistic), 1))
            graphs = np.concatenate((graphs, y_logistic), axis=1)
    except:
        pass

    expr2 = None
    edoubletime = None
    edoubletimeerror = None
    try:
        epopt, epcov = curve_fit(exponential, x_original, y_original, bounds=([0, 0, -100], [100, 0.9, 100]),
                                 maxfev=10000)
        eerror = np.sqrt(np.diag(epcov))

        # for exponential curve, slope = growth rate. so doubling time = ln(2) / growth rate
        edoubletime = np.log(2) / epopt[1]
        # standard error
        edoubletimeerror = 1.96 * edoubletime * np.abs(eerror[1] / epopt[1])

        # calculate R^2
        residuals = y_original - exponential(x_original, *epopt)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y_original - np.mean(y_original)) ** 2)
        expr2 = 1 - (ss_res / ss_tot)

        if expr2 > R2_limit:
            y_exponential = exponential(x_original, *epopt)
            y_exponential = np.reshape(np.copy(y_exponential), (len(y_exponential), 1))
            graphs = np.concatenate((graphs, y_exponential), axis=1)
    except:
        pass

    return graphs.tolist(), {
        "border": border,
        "date": co.index,
        "y_original": y_original,
        "expr2": expr2,
        "edoubletime": edoubletime,
        "edoubletimeerror": edoubletimeerror,
        "logisticr2": logisticr2,
        "ldoubletime": ldoubletime,
        "ldoubletimeerror": ldoubletimeerror
    }


if __name__ == '__main__':
    countries_data = []
    countries = [('Switzerland', 8570000)]  # , ('Germany', 82790000), ('US', 327200000), (None, 7530000000)]
    for c in countries:
        # get different figures
        default_figure, report_data = plotCases(df, 'Country/Region', c)
        # get report
        general_report = GeneralReport(**report_data).get_report()
        # add it to the countries json
        countries_data.append({
            "name": c[0],
            "key": c[0].lower(),
            "graph": default_figure,
            "report": general_report})

        # replaces a index with the date
        # x_original = [str(date.today() - timedelta(days=int(i)+1)) for i in np.arange(y_original.size)]
        # x_original.reverse()
    create_json(countries_data)
