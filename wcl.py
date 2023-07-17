import os
import logging
import requests

from statistics import mean

log = logging.getLogger(__name__)

class WCLlogs(object):
    def __init__(self, character: str):
        self.character = character
        url = 'https://classic.warcraftlogs.com:443/v1/parses/character/{0}/grobbulus/us?timeframe=historical&api_key={1}'
        self.url = url.format(character, os.environ['WCL_APIKEY'])
        r = requests.get(self.url)
        if not isinstance(r.json(), list):
            raise Exception("Unable to find character {character}: {r.json()['error']}")
        self.data = r.json()

    @property
    def id(self):
        return self.data[0]['characterID']

    @property
    def class_name(self):
        return self.data[0]['class']

    @property
    def spec(self):
        return max(set([x['spec'] for x in self.data]), key = self.data.count)

    def best(self, id: int):
        return max(set([x['percentile'] for x in self.data if x['encounterID'] == id]))

    def historical_avg(self):
        try:
            encounters = []
            for entry in self.data:
                if entry['size'] == 25:
                    encounters.append(entry['encounterID'])

            tops = []
            for enc in set(encounters):
                tops.append(self.best(enc))

            return round(mean(tops), 2)
        except Exception as e:
            raise e
