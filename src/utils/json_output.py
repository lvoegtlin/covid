import json
import os


class JSONOutput:
    __instance = None

    def __init__(self):
        if JSONOutput.__instance is not None:
            JSONOutput.get_instance()
        self.countries = []
        self.dates = []

    @staticmethod
    def get_instance():
        if JSONOutput.__instance is None:
            JSONOutput.__instance = JSONOutput()
        return JSONOutput.__instance

    def add_country(self, country, graphs, report):
        """

        :param country_data: tuple(graphs, report)
        :return:
        """
        self.countries.append((country, graphs, report))

    def create_json(self):
        countries_json = {"countries": [self._create_country_json(*country_data) for country_data in self.countries]}
        with open(os.path.join("..", "website", "data", "data.json"), "w") as f:
            json.dump(countries_json, f)

    def _create_country_json(self, country, graphs, report):
        return {
            "name": country,
            "key": country.lower(),
            "graph": graphs.get_graphs(),  # TODO change for multigraph
            "headers": graphs.headers,
            "dates": self.dates,
            "report": report
        }
