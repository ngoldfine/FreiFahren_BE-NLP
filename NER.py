# flake8: noqa

from os import pipe
import os
import spacy
from spacy.tokens import Doc
from spacy.training import Example
from spacy.language import Language
from spacy import displacy


from rapidfuzz import process, fuzz
from tqdm import tqdm

import random
import json

nlp = spacy.load('de_core_news_sm')
STATION_NAMES = []

with open('data/stations_and_lines.json', 'r') as f:
    stations_and_lines = json.load(f)

for lines in stations_and_lines:
    for station in stations_and_lines[lines]:
        STATION_NAMES.append(station)

RENDERING_OPTIONS = {"ents": ["STATION"], "colors": {"STATION": "linear-gradient(90deg, #aa9cfc, #fc9ce7)"}}
EPOCHS = 200

def train(nlp: Language, train_data: list, EPOCHS: int = EPOCHS):
    optimizer = nlp.create_optimizer()

    for _ in tqdm(range(EPOCHS), desc="Epochs", position=0, leave=True):
        random.shuffle(train_data)
        for raw_text, entity_offsets in tqdm(train_data, desc="Training data", position=0, leave=True):
            doc = nlp.make_doc(raw_text)
            example = Example.from_dict(doc, {"entities": entity_offsets})
            nlp.update([example], sgd=optimizer)

    if not os.path.exists('data/models/ner_model'):
        os.makedirs('data/models/ner_model')
    nlp.to_disk('data/models/ner_model')

def pipeline(nlp: Language, text: str):

    train_data = []

    with open('data/stations_and_lines.json', 'r') as f:
        STATION_NAMES = json.load(f)

    for lines in STATION_NAMES:
        for station in STATION_NAMES[lines]:
            train_data.append((station, [(0, len(station), "STATION")]) )
    
    # Disable all pipe components except 'ner'
    disabled_pipes = []
    for pipe_name in nlp.pipe_names:
        if pipe_name != 'ner':
            nlp.disable_pipes(pipe_name)
            disabled_pipes.append(pipe_name)
    
    train(nlp, train_data, EPOCHS)

    # Enable all previously disabled pipe components
    for pipe_name in disabled_pipes:
        nlp.enable_pipe(pipe_name)

    doc = nlp(text)
    matches = [ent.text for ent in doc.ents]

    return matches

# FUZZY PART HERE

def fuzzy_match_stations(recognized_entities, station_names):
    matches = []
    for entity in recognized_entities:
        match, score, _ = process.extractOne(entity, station_names, scorer=fuzz.token_set_ratio)
        if score > 50:
            matches.append((entity, match, score))
    return matches


def identify_stations(text, nlp: Language, station_names: list):
    doc = nlp(text)
    
    recognized_stations = pipeline(nlp, text)
    matches = fuzzy_match_stations(recognized_stations, station_names)
    return matches
