from src.figures.exponential_logistic_fitting import ExponentialLogisticFitting
from src.report.report import GeneralReport
from src.utils.data_prep import DataContainer
from src.utils.json_output import JSONOutput
from tqdm import tqdm

import numpy as np

if __name__ == '__main__':
    figureObjects = [ExponentialLogisticFitting]

    data_container = DataContainer()
    dates = data_container.get_date_list()
    json_output = JSONOutput.get_instance()
    json_output.dates = list(dates)
    json_output.countries = data_container.get_country_list()
    for country in tqdm(data_container.get_country_list()[86:87]):
        x = np.arange(dates.size)
        y = data_container.get_data()[country].values
        figures = []

        for f in figureObjects:
            figures.append(f(x, y))

        exp = next(f for f in figures if f.__class__ == ExponentialLogisticFitting)
        report = GeneralReport(dates, exp, y).get_report()
        json_output.add_country(country, figures[0], report)

    json_output.create_json()
    print("finished!!")
