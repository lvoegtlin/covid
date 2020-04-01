import json
import os


def create_json(countries_data):
    countries_json = {"countries": [country_data for country_data in countries_data]}
    with open(os.path.join("website", "data", "data.json"), "w") as f:
        json.dump(countries_json, f)