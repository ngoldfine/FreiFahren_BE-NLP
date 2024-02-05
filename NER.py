# flake8: noqa

import os
import spacy
from spacy.tokens import Doc
from spacy.training import Example
from spacy.language import Language
from spacy import displacy
import ner_lstm

from rapidfuzz import process, fuzz
from tqdm import tqdm

import random
import json

from fuzzy import fuzzy_stations

RENDERING_OPTIONS = {"ents": ["STATION"], "colors": {"STATION": "linear-gradient(90deg, #aa9cfc, #fc9ce7)"}}
EPOCHS = 1

SHOULD_WE_TRAIN = True
MODEL_PATH = 'data/testlol'

# MAIN_TRAIN_DATA = [
#     ["s-bahn kontrolleure friedrichstrasse 2mal weiblich eine kräftig und blonde haare lang andere dünner grüne jacke",
#         {"entities":[(20,36,"STATION")]}],
#     ["4 Kontrolleur*innen S85 nach Buch",
#         {"entities":[(20,23,"LINE"),(29,33,"STATION")]}],
#     ["Sind nicht zu übersehen 😅",
#         {"entities":[]}],
#     ["U5 nach Hönow",
#         {"entities":[(0,2,"LINE"),(8,13,"STATION")]}],
#     ["Blaue veste",
#         {"entities":[]}],
#     ["S42 grade landsbergeralee los",
#         {"entities":[(0,3,"LINE"),(10,25,"STATION")]}],
#     ["froilein rattenmeier sie/shehey kurze frage: der kontroletti hat meinen namen falsch geschrieben, adresse stimmt aber. kann das ...Wenn deine Ausweisnummer stimmt finden die dich überall in der EU außer in Rumänien 😬",
#         {"entities":[]}],
#     ["FlinnUnd wenn er den Namen hat aber nicht die Adresse?Die Ausweisnummer bzw das Personaldokument worüber sie dich aufgenommen haben ist entscheidend",
#         {"entities":[]}],
#     ["zwei bos westen mit gelbem nacken sind gerade schönleinstr u8 richtung hermannstr eingestiegen",
#         {"entities":[(46,58,"STATION"),(59,61,"LINE"),(71,81,"STATION")]}],
#     ["3 bos u8 richtung wittenau, weinmeisterstr ausgestiegen",
#         {"entities":[(6,8,"LINE"),(18,26,"STATION"),(28,42,"STATION")]}],
#     ["Große Kontrolle beim aussteigen an der U-Alt-Tempelhof U6",
#         {"entities":[(39,54,"STATION"),(55,57,"LINE")]}],
#     ["Ring, tempelhof, richtung sudkreuz",
#         {"entities":[(6,15,"STATION"),(26,34,"STATION")]}],
#     ["u8 Voltastr.",
#         {"entities":[(0,2,"LINE"),(3,11,"STATION")]}],
#     ["mind. 2 blaue westen am leopoldplatz, polizei ist auch da, am u9 gleis",
#         {"entities":[(24,36,"STATION"),(62,64,"LINE")]}],
#     ["Neukölln  sbahn 2 männlich gelesene",
#         {"entities":[(0,8,"STATION")]}],
#     ["Lazi ♀️Neukölln  sbahn 2 männlich geleseneBeide glatze",
#         {"entities":[(5,15,"STATION")]}],
#     ["Jetzt noch zusätzlich zwei weitere steigen von s41 aus in Tempelhof",
#         {"entities":[(47,50,"LINE"),(58,67,"STATION")]}],
#     ["2 Männer mit blauen Westen stiegen in die U8 Richtung Witteneu @ Henrich-Heine-Straße ein",
#         {"entities":[(42,44,"LINE"),(54,62,"STATION"),(65,85,"STATION")]}],
#     ["S7 Richtung potsdam Hbf, 3 w gelesen, gleich griebnitzsee",
#         {"entities":[(0,2,"LINE"),(12,23,"STATION"),(45,57,"STATION")]}]]

if not os.path.exists(f'{MODEL_PATH}'):
        os.makedirs(f'{MODEL_PATH}')
        print(f"Path did not exist, creating now {MODEL_PATH}")



# WENN DU TRAINIERST, DANN LADE DE_CORE_NEWS_SM UND MACHE train() in pipeline() ENTKOMMENTIERT, SONST LADE DAS MODEL

if SHOULD_WE_TRAIN:
    nlp = spacy.load('de_core_news_md')

else:
    # nlp = spacy.load('de_core_news_md')   
    nlp = spacy.load(f'{MODEL_PATH}') # eigentlich
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

    # for array in MAIN_TRAIN_DATA:
    #     train_data.append(array)
    
    print(train_data)

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
    

    # recognized_stations = pipeline(nlp, text)

    recognized_stations = ner_lstm.identify_stations(text)
    print("INPUT -> recognized from NER: ", recognized_stations)
    matches = fuzzy_match_stations(recognized_stations)
    print("NER -> recognized from FUZZY: ", matches)
    if len(matches) > 0:
        return matches[0]
    else:
        return None

print(identify_stations("s-bahn kontrolleure friedrichstrasse 2mal weiblich eine kräftig und blonde haare lang andere dünner grüne jacke"))
