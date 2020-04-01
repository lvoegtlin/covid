import numpy as np


class GeneralReport:

    def __init__(self, border, date, y_original,
                 expr2, edoubletime, edoubletimeerror,
                 logisticr2, ldoubletime, ldoubletimeerror):
        self.report = []
        self.border = border
        self.date = date
        self.expr2 = expr2
        self.edoubletime = edoubletime
        self.edoubletimeerror = edoubletimeerror
        self.logisticr2 = logisticr2
        self.ldoubletime = ldoubletime
        self.ldoubletimeerror = ldoubletimeerror
        self.current = y_original[-1]
        self.lastweek = y_original[-8]
        self.two_weeks_ago = y_original[-15]

    def get_report(self):
        if not self.report:
            self._create_report()
        return self.report

    def _create_key_values(self):
        ratio = self.current / self.lastweek
        two_weeks_ratio = self.lastweek / self.two_weeks_ago
        dailypercentchange = round(100 * (pow(ratio, 1 / 7) - 1), 1)
        dailypercentchange_two_weeks = round(100 * (pow(two_weeks_ratio, 1 / 7) - 1), 1)
        recentdbltime = round(7 * np.log(2) / np.log(ratio), 1)
        recentdbltime_two_weeks = round(7 * np.log(2) / np.log(two_weeks_ratio), 1)

        return {"ratio": ratio,
                "two_weeks_ratio": two_weeks_ratio,
                "dailypercentchange": dailypercentchange,
                "dailypercentchange_two_weeks": dailypercentchange_two_weeks,
                "recentdbltime": recentdbltime,
                "recentdbltime_two_weeks": recentdbltime_two_weeks}

    def _create_report(self):
        values = self._create_key_values()
        if self.current > self.lastweek:
            self.report.append(f"Starting point: {self.border} people infected<br/>")
            self.report.append('\n<h2>Based on Most Recent Week of Data</h2>\n')
            self.report.append(f'\tConfirmed cases on {self.date[-1]}: <b>{self.current}</b>\n')
            self.report.append(f'\tConfirmed cases on {self.date[-8]} <b>{self.lastweek}</b>\n')
            self.report.append(f'\tConfirmed cases on {self.date[-15]} <b>{self.two_weeks_ago}</b>\n')
            self.report.append(f'\tRatio (current/last): <b>{round(values["ratio"], 2)}</b>\n')
            self.report.append(f'\tRatio (lastweek/two_weeks_ago): <b>{round(values["two_weeks_ratio"], 2)}</b>\n')
            self.report.append(f'\tWeekly increase (last-current): <b>{round(100 * (values["ratio"] - 1), 1)}%</b>\n')
            self.report.append(
                f'\tWeekly increase (2_weeks_ago-last): <b>{round(100 * (values["two_weeks_ratio"] - 1), 1)}%</b>\n')
            self.report.append(f'\tDaily increase (last-current): <b>{values["dailypercentchange"]}%</b> per day\n')
            self.report.append(
                f'\tDaily increase (2_weeks_ago-last): <b>{values["dailypercentchange_two_weeks"]}%</b> per day\n')
            self.report.append(
                f'\tDoubling Time [last-current] (represents recent growth): <b>{values["recentdbltime"]}</b> days\n')
            self.report.append(
                f'\tDoubling Time [2_weeks_ago-last] (represents recent growth): <b>{values["recentdbltime_two_weeks"]}</b> days\n')

            if self.expr2 is not None or self.edoubletime is not None or self.edoubletimeerror is not None:
                self.report.append('<h2>Based on Exponential Fit</h2>\n')
                self.report.append(f'\tR&#178;: <b>{self.expr2}</b>\n')
                self.report.append(f'\tDoubling Time (represents overall growth): '
                                   f'<b>{round(self.edoubletime, 2)} (&plusmn; {round(self.edoubletimeerror, 2)})</b> days\n')

            if self.logisticr2 is not None or self.ldoubletime is not None or self.ldoubletimeerror is not None:
                self.report.append('<h2>Based on Logistic Fit</h2>\n')
                self.report.append(f'\tR&#178;: <b>{self.logisticr2}</b>\n')
                self.report.append(f'\tDoubling Time (during middle of growth): '
                                   f'<b>{round(self.ldoubletime, 2)} (&plusmn; {round(self.ldoubletimeerror, 2)})</b> days\n')
