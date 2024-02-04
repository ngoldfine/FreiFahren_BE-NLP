# flake8: noqa

import spacy
from spacy import displacy
from rapidfuzz import process, fuzz

import json

# Load spaCy model
nlp = spacy.blank("de")
ner = nlp.add_pipe("ner")

nlp.begin_training()

station_names = ['potsdam Hbf', 'Gleisdreieck', 'Kurfürstenstraße']
station_names = [(name, "STATION") for name in station_names]

def fuzzy_match_stations(recognized_entities, station_names):
    matches = []
    for entity in recognized_entities:
        match, score, _ = process.extractOne(entity, station_names, scorer=fuzz.token_set_ratio)
        print(match, score, entity)
        if score > 10:
            matches.append((entity, match, score))
    return matches


def identify_stations(text):
    doc = nlp(text)
    
    recognized_stations = [ent for ent in doc.ents if ent.label_ in ["LOC", "STATION"]]  # Adjust based on your model
    print(recognized_stations)
    matches = fuzzy_match_stations(recognized_stations, station_names)
    return matches

identify_stations('S7 Richtung potsdam Hbf, 3 w gelesen, gleich griebnitzsee')
