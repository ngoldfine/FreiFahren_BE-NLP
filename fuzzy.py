# flake8: noqa


from requests import get
import spacy 
from spacy.matcher import Matcher
from spacy.tokens import Span
import json

with open('data/stations_and_lines.json') as file:
    stations_and_lines = json.load(file)

STATIONS = []

for lines in stations_and_lines:
    for stations in stations_and_lines[lines]:
        STATIONS.append(stations)

nlp = spacy.load('de_core_news_md')

matcher = Matcher(nlp.vocab)

patterns = []

for station in STATIONS:
    station_lower = station.lower()
    
    matcher.add(f"{station}", [[{"LOWER": {"FUZZY": station_lower}}]])

def fuzzy(text):
    doc = nlp(text)
    matches = matcher(doc)
    
    
        
    matchList = []

    for match_id, start, end in matches:
        matchList.append(nlp.vocab.strings[match_id])


    if len(matchList) > 0:
        return matchList[0]
    else:
        return None

def fuzzy_stations(recognized_stations):
    matches = []
    for stations in recognized_stations:
        matches.append(fuzzy(stations))
    
    return matches
        

def getSimilar(stationName):
    doc1 = nlp(stationName.lower())
    nearest = ["", 0]

    for station in STATIONS:
        if doc1.similarity(nlp(station.lower())) > nearest[1]:
            nearest[0] = nlp(station.lower())
            nearest[1] = doc1.similarity(nlp(station.lower()))
    return nearest[0]

