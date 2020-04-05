import numpy as np


class GeneralReport:

    def __init__(self, dates, exp, y):
        self.report = []
        self.date = dates
        self.expr2 = exp.expr2
        self.edoubletime = exp.edoubletime
        self.edoubletimeerror = exp.edoubletimeerror
        self.logisticr2 = exp.logisticr2
        self.ldoubletime = exp.ldoubletime
        self.ldoubletimeerror = exp.ldoubletimeerror
        self.current = y[-1]
        self.lastweek = y[-8]
        self.two_weeks_ago = y[-15]

    def get_report(self):
        if not self.report:
            self._create_report()
        return self.report

    def _create_key_values(self):
        ratio = self.current / self.lastweek if self.lastweek != 0 else None
        two_weeks_ratio = self.lastweek / self.two_weeks_ago \
            if self.two_weeks_ago != 0 else None
        dailypercentchange = round(100 * (pow(ratio, 1 / 7) - 1), 1) if ratio is not None else None
        dailypercentchange_two_weeks = round(100 * (pow(two_weeks_ratio, 1 / 7) - 1), 1) \
            if two_weeks_ratio is not None else None
        recentdbltime = round(7 * np.log(2) / np.log(ratio), 1) if ratio is not None and ratio != 1 else None
        recentdbltime_two_weeks = round(7 * np.log(2) / np.log(two_weeks_ratio), 1) \
            if two_weeks_ratio is not None and two_weeks_ratio != 1 else None

        return {"ratio": ratio,
                "two_weeks_ratio": two_weeks_ratio,
                "dailypercentchange": dailypercentchange,
                "dailypercentchange_two_weeks": dailypercentchange_two_weeks,
                "recentdbltime": recentdbltime,
                "recentdbltime_two_weeks": recentdbltime_two_weeks}

    def _create_report(self):
        values = self._create_key_values()
        if self.current > self.lastweek:
            self.report.append('\n<h2>Based on Most Recent Week of Data</h2>\n')
            self.report.append(f'\tConfirmed cases on {self.date[-1]}: <b>{self.current}</b>\n')
            self.report.append(f'\tConfirmed cases on {self.date[-8]} <b>{self.lastweek}</b>\n')
            self.report.append(f'\tConfirmed cases on {self.date[-15]} <b>{self.two_weeks_ago}</b>\n')
            self.report.append(f'\tRatio (current/last): <b>{round(values["ratio"], 2)}</b>\n') \
                if values["ratio"] is not None else None
            self.report.append(f'\tRatio (lastweek/two_weeks_ago): <b>{round(values["two_weeks_ratio"], 2)}</b>\n') \
                if values["two_weeks_ratio"] is not None else None
            self.report.append(f'\tWeekly increase (last-current): <b>{round(100 * (values["ratio"] - 1), 1)}%</b>\n') \
                if values["ratio"] is not None else None
            self.report.append(
                f'\tWeekly increase (2_weeks_ago-last): <b>{round(100 * (values["two_weeks_ratio"] - 1), 1)}%</b>\n') \
                if values["two_weeks_ratio"] is not None else None
            self.report.append(f'\tDaily increase (last-current): <b>{values["dailypercentchange"]}%</b> per day\n') \
                if values["ratio"] is not None else None
            self.report.append(
                f'\tDaily increase (2_weeks_ago-last): <b>{values["dailypercentchange_two_weeks"]}%</b> per day\n') \
                if values["two_weeks_ratio"] is not None else None
            self.report.append(
                f'\tDoubling Time [last-current] (represents recent growth): <b>{values["recentdbltime"]}</b> days\n') \
                if values["ratio"] is not None else None
            self.report.append(
                f'\tDoubling Time [2_weeks_ago-last] (represents recent growth): <b>{values["recentdbltime_two_weeks"]}</b> days\n') \
                if values["two_weeks_ratio"] is not None else None

            if self.expr2 != 0 or self.edoubletime != 0 or self.edoubletimeerror != 0:
                self.report.append('<h2>Based on Exponential Fit</h2>\n')
                self.report.append(f'\tR&#178;: <b>{self.expr2}</b>\n')
                self.report.append(f'\tDoubling Time (represents overall growth): '
                                   f'<b>{round(self.edoubletime, 2)} (&plusmn; {round(self.edoubletimeerror, 2)})</b> days\n')

            if self.logisticr2 != 0 or self.ldoubletime != 0 or self.ldoubletimeerror != 0:
                self.report.append('<h2>Based on Logistic Fit</h2>\n')
                self.report.append(f'\tR&#178;: <b>{self.logisticr2}</b>\n')
                self.report.append(f'\tDoubling Time (during middle of growth): '
                                   f'<b>{round(self.ldoubletime, 2)} (&plusmn; {round(self.ldoubletimeerror, 2)})</b> days\n')
