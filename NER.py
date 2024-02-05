# flake8: noqa

from os import pipe
import os
from xmlrpc.client import TRANSPORT_ERROR
import spacy
from spacy.tokens import Doc
from spacy.training import Example
from spacy.language import Language
from spacy import displacy


from rapidfuzz import process, fuzz
from tqdm import tqdm

import random
import json

from fuzzy import fuzzy_stations

RENDERING_OPTIONS = {"ents": ["STATION"], "colors": {"STATION": "linear-gradient(90deg, #aa9cfc, #fc9ce7)"}}
EPOCHS = 20

SHOULD_WE_TRAIN = False
MODEL_PATH = 'data/models/ner_model'



if not os.path.exists(f'{MODEL_PATH}'):
        os.makedirs(f'{MODEL_PATH}')
        print(f"Path did not exist, creating now {MODEL_PATH}")


# WENN DU TRAINIERST, DANN LADE DE_CORE_NEWS_SM UND MACHE train() in pipeline() ENTKOMMENTIERT, SONST LADE DAS MODEL

if SHOULD_WE_TRAIN:
    nlp = spacy.load('de_core_news_md')
else:
    nlp = spacy.load('de_core_news_md')   
    # nlp = spacy.load(f'{MODEL_PATH}') # eigentlich
    # print(f"Loaded from {MODEL_PATH}")


STATION_NAMES = []

with open('data/stations_and_lines.json', 'r') as f:
    stations_and_lines = json.load(f)

for lines in stations_and_lines:
    for station in stations_and_lines[lines]:
        STATION_NAMES.append(station)

def train(nlp: Language, EPOCHS: int = EPOCHS):

    if SHOULD_WE_TRAIN == False:
        return print("ACTIVATE SHOULD_WE_TRAIN PLEASE")
    
    train_data = []

    
    for station in STATION_NAMES:
        train_data.append((station, [(0, len(station), "STATION")]) )



    optimizer = nlp.create_optimizer()

    for _ in tqdm(range(EPOCHS), desc="Epochs", position=0, leave=True):
        random.shuffle(train_data)
        for raw_text, entity_offsets in tqdm(train_data, desc="Training data", position=0, leave=True):
            doc = nlp.make_doc(raw_text)
            example = Example.from_dict(doc, {"entities": entity_offsets})
            nlp.update([example], sgd=optimizer)

    # COMMENT OR NO COMMENT / TRAIN OR NO TRAIN
    if SHOULD_WE_TRAIN:
        nlp.to_disk(f'{MODEL_PATH}')
        print(f"SAVED TO DISK {MODEL_PATH}")

def pipeline(nlp: Language, text: str):
 
    # Disable all pipe components except 'ner'
    disabled_pipes = []
    for pipe_name in nlp.pipe_names:
        if pipe_name != 'ner':
            nlp.disable_pipes(pipe_name)
            disabled_pipes.append(pipe_name)
    
    # COMMENT OR NO COMMENT / TRAIN OR NO TRAIN
    if SHOULD_WE_TRAIN:
        train(nlp, EPOCHS)

    # Enable all previously disabled pipe components
    for pipe_name in disabled_pipes:
        nlp.enable_pipe(pipe_name)

    doc = nlp(text)
    matches = [ent.text for ent in doc.ents]

    return matches

# FUZZY PART HERE

def fuzzy_match_stations(recognized_entities):
    matches = []
    for entity in recognized_entities:
        match, score, _ = process.extractOne(entity, STATION_NAMES, scorer=fuzz.token_set_ratio)
        if score > 10:
            matches.append(match)
            print(f"Matched '{entity}' to '{match}' with a score of {score}")
    
    return matches


def identify_stations(text):
    

    recognized_stations = pipeline(nlp, text)
    print("INPUT -> recognized from NER: ", recognized_stations)
    matches = fuzzy_match_stations(recognized_stations)
    print("NER -> recognized from FUZZY: ", matches)
    if len(matches) > 0:
        return matches
    else:
        return None

message = "U6, alt-Tempelhofff, gemischt in Zivil und mit BVG-Jacke."

print(identify_stations(message))

