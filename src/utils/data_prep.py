import pandas as pd
import numpy as np


class DataContainer:

    def __init__(self):
        self._get_ch_data()
        self._get_who_data()
        self._prepare_data()

    def _get_who_data(self):
        self.who_data = pd.read_csv(
            'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

    def _get_ch_data(self):
        self.ch_data = pd.read_csv(
            'https://raw.githubusercontent.com/daenuprobst/'
            'covid19-cases-switzerland/master/covid19_cases_switzerland_openzh.csv').iloc[:, -1]

    def get_country_list(self):
        return list(self.who_data.columns)

    def get_date_list(self):
        return self.who_data.T.columns.values

    def _prepare_data(self):
        """
        Prepares the data in a consistent fashion.

        The data looks like follow:

        country | day_1 | day_2 | ... | day_n |

        :return: pandas.dataframe

        """
        # get the data in the form county country | day_1 | day_2 | ... | day_n |
        # but still have multiple entries for china etc
        self.who_data = self.who_data.drop(columns=["Province/State", "Lat", "Long"])
        # sum up all entries from the same country
        self.who_data = self.who_data.groupby("Country/Region").sum().T
        # prepare swiss data
        self._add__switzerland_data()
        # add world_wide data
        self._add_world_wide()

    def _add__switzerland_data(self):
        for i, d in enumerate(np.flip(self.ch_data.values)):
            if i == 0:
                continue
            self.who_data['Switzerland'][self.who_data.shape[0] - i] = d

    def get_data(self):
        return self.who_data

    def _add_world_wide(self):
        self.who_data['World Wide'] = self.who_data.sum(axis=1).values
