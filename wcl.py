import os
import logging
import requests

from statistics import mean

log = logging.getLogger(__name__)

def parse_logs(character):
    try:
        url = 'https://classic.warcraftlogs.com:443/v1/parses/character/{0}/grobbulus/us?api_key={1}'
        r = requests.get(url.format(character, os.environ['WCL_APIKEY']))
        if not isinstance(r.json(), list):
            return

        encounters = []
        for entry in r.json():
            if entry['size'] == 25:
                encounters.append((entry['encounterID'], entry['percentile']))

        log.info(encounters)

        tops = []
        for enc in set([x[0] for x in encounters]):
            parses = [x[1] for x in encounters if x[0] == enc]
            tops.append(max(parses))

        log.info(tops)

        return round(mean(tops), 2)
    except Exception as e:
        log.error(f'parse_logs,{type(e)},{e}', exc_info=True)
