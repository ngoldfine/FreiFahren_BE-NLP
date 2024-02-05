# flake8: noqa
import spacy
import random
import os
from datetime import datetime
from spacy.training import Example
from data.ANNOTATED_MESSAGES_LSTM import ANNOTATED_DATA
from fuzzywuzzy import process, fuzz
import json

TRAIN_DATA = [
    ["s-bahn kontrolleure friedrichstrasse 2mal weiblich eine kräftig und blonde haare lang andere dünner grüne jacke",
        {"entities":[(20,36,"STATION")]}],
    ["4 Kontrolleur*innen S85 nach Buch",
        {"entities":[(20,23,"LINE"),(29,33,"STATION")]}],
    ["Sind nicht zu übersehen 😅",
        {"entities":[]}],
    ["U5 nach Hönow",
        {"entities":[(0,2,"LINE"),(8,13,"STATION")]}],
    ["Blaue veste",
        {"entities":[]}],
    ["S42 grade landsbergeralee los",
        {"entities":[(0,3,"LINE"),(10,25,"STATION")]}],
    ["froilein rattenmeier sie/shehey kurze frage: der kontroletti hat meinen namen falsch geschrieben, adresse stimmt aber. kann das ...Wenn deine Ausweisnummer stimmt finden die dich überall in der EU außer in Rumänien 😬",
        {"entities":[]}],
    ["FlinnUnd wenn er den Namen hat aber nicht die Adresse?Die Ausweisnummer bzw das Personaldokument worüber sie dich aufgenommen haben ist entscheidend",
        {"entities":[]}],
    ["zwei bos westen mit gelbem nacken sind gerade schönleinstr u8 richtung hermannstr eingestiegen",
        {"entities":[(46,58,"STATION"),(59,61,"LINE"),(71,81,"STATION")]}],
    ["3 bos u8 richtung wittenau, weinmeisterstr ausgestiegen",
        {"entities":[(6,8,"LINE"),(18,26,"STATION"),(28,42,"STATION")]}],
    ["Große Kontrolle beim aussteigen an der U-Alt-Tempelhof U6",
        {"entities":[(39,54,"STATION"),(55,57,"LINE")]}],
    ["Ring, tempelhof, richtung sudkreuz",
        {"entities":[(6,15,"STATION"),(26,34,"STATION")]}],
    ["u8 Voltastr.",
        {"entities":[(0,2,"LINE"),(3,11,"STATION")]}],
    ["mind. 2 blaue westen am leopoldplatz, polizei ist auch da, am u9 gleis",
        {"entities":[(24,36,"STATION"),(62,64,"LINE")]}],
    ["Neukölln  sbahn 2 männlich gelesene",
        {"entities":[(0,8,"STATION")]}],
    ["Lazi ♀️Neukölln  sbahn 2 männlich geleseneBeide glatze",
        {"entities":[(5,15,"STATION")]}],
    ["Jetzt noch zusätzlich zwei weitere steigen von s41 aus in Tempelhof",
        {"entities":[(47,50,"LINE"),(58,67,"STATION")]}],
    ["2 Männer mit blauen Westen stiegen in die U8 Richtung Witteneu @ Henrich-Heine-Straße ein",
        {"entities":[(42,44,"LINE"),(54,62,"STATION"),(65,85,"STATION")]}],
    ["S7 Richtung potsdam Hbf, 3 w gelesen, gleich griebnitzsee",
        {"entities":[(0,2,"LINE"),(12,23,"STATION"),(45,57,"STATION")]}]
    ]


for data in ANNOTATED_DATA['annotations']:
    TRAIN_DATA.append(data)

# for data in TRAIN_DATA:
#     print(data)
    
# Load a blank English model
nlp = spacy.blank("de")

# Add the NER component to the pipeline
ner = nlp.create_pipe("ner")
nlp.add_pipe('ner')

# Add your specific labels to the NER component
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Assuming TRAIN_DATA is a list of tuples, each containing a text and a dictionary of annotations
examples = [Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in TRAIN_DATA]

def train(EPOCHS=1):

    # Train the model
    optimizer = nlp.initialize()
    for itn in range(EPOCHS):
        random.shuffle(examples)
        losses = {}
        for example in examples:
            nlp.update([example], sgd=optimizer, drop=0.35, losses=losses)
        print(losses)
    
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y___%H.%M.%S")

    if not os.path.exists(f'models/{dt_string}_EPOCHS_{EPOCHS}'):
        os.makedirs(f'models/{dt_string}_EPOCHS_{EPOCHS}')
    
    nlp.to_disk(f'models/{dt_string}_EPOCHS_{EPOCHS}')
    print(f'saved model to models/{dt_string}_EPOCHS_{EPOCHS}')
    

# Use the Scorer class to score the train examples
# scorer = nlp.evaluate(examples)
STATION_NAMES = []

with open('data/stations_and_lines.json', 'r') as f:
    stations_and_lines = json.load(f)

for lines in stations_and_lines:
    for station in stations_and_lines[lines]:
        STATION_NAMES.append(station)

def fuzzy_match_stations(recognized_entities):
    matches = []
    for entity in recognized_entities:
        match, score = process.extractOne(entity, STATION_NAMES, scorer=fuzz.token_set_ratio)
        if score > 10:
            matches.append(match)
            # print(f"Matched '{entity}' to '{match}' with a score of {score}")
    
    return matches
        
def identify_stations(text):
  nlp.from_disk('models/05-02-2024___23.32.17_EPOCHS1')
  match = nlp(text)
  matches = []
  for ent in match.ents:
      matches.append(ent.label_)

  
  return matches



def testANNOTS():
    tagCount = 0
    correctCount = 0
    for dataset in ANNOTATED_DATA['annotations']:
        for data in dataset:
            test = []
            if type(data) == str:
              print(f"Message: {data}")
              test_message = identify_stations(data)
        
            if type(data) == dict:
              for item in data['entities']:
                  tagCount += 1
                  if item[2] in test_message:
                      correctCount += 1
          
    print(f"\nResult: {correctCount/tagCount} Tags: {tagCount} Correct annots: {correctCount}" )

def testTrain():
    tagCount = 0
    correctCount = 0
    for dataset in TRAIN_DATA:
        for data in dataset:
            test = []
            if type(data) == str:
              print(f"Message: {data}")
              test_message = identify_stations(data)
        
            if type(data) == dict:
              for item in data['entities']:
                  tagCount += 1
                  if item[2] in test_message:
                      correctCount += 1
          
    print(f"\nResult: {correctCount/tagCount} Tags: {tagCount} Correct annots: {correctCount}" )


testTrain()