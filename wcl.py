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
        if not r.json():
            raise IndexError("No current parses")
        if 'error' in r.json():
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
        return max([x['spec'] for x in self.data])

    def highest_ilvl(self):
        return max(set([x['ilvlKeyOrPatch'] for x in self.data]))

    def heroic_count(self):
        encounters = set([x['encounterID'] for x in self.data if x['size'] == 25 and x['difficulty'] == 4])
        return len(encounters)

    def best_of25H(self, id: int):
        return max(set([x['percentile'] for x in self.data if x['encounterID'] == id and x['size'] == 25 and x['difficulty'] == 4]))

    def historical_avg(self):
        try:
            encounters = []
            for entry in self.data:
                if entry['size'] == 25 and entry['difficulty'] == 4:
                    encounters.append(entry['encounterID'])

            tops = []
            for enc in set(encounters):
                if enc != 637:
                    tops.append(self.best_of25H(enc))

            return round(mean(tops), 2)
        except Exception as e:
            raise e
