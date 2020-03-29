import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb

from PIL import Image, ImageDraw
from scipy.optimize import curve_fit

df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')


def logistic(t, a, b, c, d):
    return c + (d - c) / (1 + a * np.exp(- b * t))


def exponential(t, a, b, c):
    return a * np.exp(b * t) + c


def plotCases(dataframe, column, country):
    if country is None:
        co = dataframe.iloc[:, 4:].T.sum(axis=1)
        country = 'WorldWide'
    elif country == 'Switzerland':
        co = pd.read_csv(
            'https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/covid19_cases_switzerland_openzh.csv').iloc[
             :, -1]

    else:
        co = dataframe[dataframe[column] == country].iloc[:, 4:].T.sum(axis=1)
    co = pd.DataFrame(co)
    co.columns = ['Cases']
    co = co.loc[co['Cases'] > 0]

    y = np.array(co['Cases'])
    x = np.arange(y.size)

    sb.set_style("darkgrid")
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, 'ko', label="Original Data")

    try:
        lpopt, lpcov = curve_fit(logistic, x, y, maxfev=10000)
        lerror = np.sqrt(np.diag(lpcov))

        # for logistic curve at half maximum, slope = growth rate/2. so doubling time = ln(2) / (growth rate/2)
        ldoubletime = np.log(2) / (lpopt[1] / 2)
        # standard error
        ldoubletimeerror = 1.96 * ldoubletime * np.abs(lerror[1] / lpopt[1])

        # calculate R^2
        residuals = y - logistic(x, *lpopt)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        logisticr2 = 1 - (ss_res / ss_tot)

    except:
        pass

    try:
        epopt, epcov = curve_fit(exponential, x, y, bounds=([0, 0, -100], [100, 0.9, 100]), maxfev=10000)
        eerror = np.sqrt(np.diag(epcov))

        # for exponential curve, slope = growth rate. so doubling time = ln(2) / growth rate
        edoubletime = np.log(2) / epopt[1]
        # standard error
        edoubletimeerror = 1.96 * edoubletime * np.abs(eerror[1] / epopt[1])

        # calculate R^2
        residuals = y - exponential(x, *epopt)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        expr2 = 1 - (ss_res / ss_tot)

    except:
        pass

    create_markdown_report(x, y, co, country, logisticr2, expr2, lpopt, ldoubletime, ldoubletimeerror, epopt, edoubletime, edoubletimeerror)

    plt.xlabel('Days', fontsize="x-large")
    plt.ylabel('Total Cases', fontsize="x-large")
    plt.legend(fontsize="x-large")
    plt.savefig(os.path.join('docs', 'images',
                             'figure_' + country + '.png'))


def create_markdown_report(x, y, co, country, logisticr2, expr2, lpopt, ldoubletime, ldoubletimeerror, epopt, edoubletime, edoubletimeerror):
    current = y[-1]
    lastweek = y[-8]
    two_weeks_ago = y[-15]

    content = []

    if current > lastweek:
        content.append('\n## Based on Most Recent Week of Data \n')
        content.append("")
        content.append(f'\tConfirmed cases on {co.index[-1]} \t {current}\n')
        content.append(f'\tConfirmed cases on {co.index[-8]} \t {lastweek}\n')
        content.append(f'\tConfirmed cases on {co.index[-15]} \t {two_weeks_ago}\n')
        ratio = current / lastweek
        two_weeks_ratio = lastweek / two_weeks_ago
        content.append(f'\tRatio (current/last): {round(ratio, 2)}\n')
        content.append(f'\tRatio (lastweek/two_weeks_ago): {round(two_weeks_ratio, 2)}\n')
        content.append(f'\tWeekly increase (last-current): {round(100 * (ratio - 1), 1)} %\n')
        content.append(f'\tWeekly increase (2_weeks_ago-last): {round(100 * (two_weeks_ratio - 1), 1)} %\n')
        dailypercentchange = round(100 * (pow(ratio, 1 / 7) - 1), 1)
        content.append(f'\tDaily increase (last-current): {dailypercentchange} % per day\n')
        dailypercentchange_two_weeks = round(100 * (pow(two_weeks_ratio, 1 / 7) - 1), 1)
        content.append(f'\tDaily increase (2_weeks_ago-last): {dailypercentchange_two_weeks} % per day\n')
        recentdbltime = round(7 * np.log(2) / np.log(ratio), 1)
        content.append(f'\tDoubling Time [last-current] (represents recent growth): {recentdbltime} days\n')
        recentdbltime_two_weeks = round(7 * np.log(2) / np.log(two_weeks_ratio), 1)
        content.append(f'\tDoubling Time [2_weeks_ago-last] (represents recent growth): {recentdbltime_two_weeks} days\n')

        if logisticr2 > 0.8:
            content.append('\n')
            plt.plot(x, logistic(x, *lpopt), 'b--', label="Logistic Curve Fit")
            content.append('\n## Based on Logistic Fit\n')
            content.append("")
            content.append(f'\tR^2:{logisticr2}\n')
            content.append(f'\tDoubling Time (during middle of growth): '
                           f'{round(ldoubletime, 2)} (± {round(ldoubletimeerror, 2)}) days\n')

        if expr2 > 0.8:
            content.append("\n")
            plt.plot(x, exponential(x, *epopt), 'r--', label="Exponential Curve Fit")
            content.append('\n## Based on Exponential Fit \n')
            content.append("")
            content.append(f'\tR^2: {expr2}\n')
            content.append(f'\tDoubling Time (represents overall growth): '
                           f'{round(edoubletime, 2)} (± {round(edoubletimeerror, 2)} ) days\n')
    # write with pillo a image with write background
    img = Image.new('RGB', (450, 380), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(content):
        d.text((10, 15*(i+1)), l, fill=(0, 0, 0))
    img.save(os.path.join('docs', 'reports', 'report_' + country + '.png'))


if __name__ == '__main__':
    countries = ['Switzerland', 'Germany', None]
    for c in countries:
        plotCases(df, 'Country/Region', c)
