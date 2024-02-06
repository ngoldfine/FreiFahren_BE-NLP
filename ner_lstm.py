
# flake8: noqa
import spacy
from spacy import displacy
import random
import os
from datetime import datetime
from spacy.training import Example
from data.ANNOTATED_MESSAGES_LSTM import ANNOTATED_DATA

import json

TRAIN_DATA = []

TEST_DATA = [["s-bahn kontrolleure friedrichstrasse 2mal weiblich eine kräftig und blonde haare lang andere dünner grüne jacke",
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
        {"entities":[(0,2,"LINE"),(12,23,"STATION"),(45,57,"STATION")]}]]

# GETTING MESSAGES DATA
for data in ANNOTATED_DATA['annotations']:
    TRAIN_DATA.append(data)

# GETTING ALL THE SYNONYMS
with open('data/data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

for station in data['sBahn_stations_with_synomyms']:
    for synonyms in data['sBahn_stations_with_synomyms'][f'{station}']:
       TRAIN_DATA.append([synonyms, {'entities': [[0, len(synonyms), "STATION"]]}])

for station in data['uBahn_stations_with_synomyms']:
    for synonyms in data['uBahn_stations_with_synomyms'][f'{station}']:
       TRAIN_DATA.append([synonyms, {'entities': [[0, len(synonyms), "STATION"]]}])

# GETTING ALL THE FORMAL LINES AND STATIONS

with open('data/stations_and_lines.json', 'r', encoding='utf-8') as file:
   stations_and_lines = json.load(file)

for lines in stations_and_lines:
  for station in stations_and_lines[f'{lines}']:
    TRAIN_DATA.append([station, {"entities": [[0, len(station), "STATION"]]}])  

# Load a blank English model
nlp = spacy.blank("de")

# Add the NER component to the pipeline
ner = nlp.create_pipe("ner")
nlp.add_pipe('ner')


# Add your specific labels to the NER component
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

def train(EPOCHS=5, until_loss=10, DATASET=TRAIN_DATA, suffix=""):
    # Assuming TRAIN_DATA is a list of tuples, each containing a text and a dictionary of annotations
    examples = [Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in DATASET]

    epoch_count = 0
    # Train the model
    optimizer = nlp.initialize()
    for itn in range(EPOCHS):
        random.shuffle(examples)
        losses = {}
        for example in examples:
            nlp.update([example], sgd=optimizer, drop=0.35, losses=losses)
        
        if losses['ner'] < until_loss:
          print("stopping at: ", losses)
          break
        epoch_count +=1
        print(losses)
        
    
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y___%H.%M.%S")
    MODEL_PATH = f'models/{dt_string}_EPOCHS_{epoch_count}_{suffix}'

    if not os.path.exists(f'models/{dt_string}_EPOCHS_{epoch_count}_{suffix}'):
        os.makedirs(f'models/{dt_string}_EPOCHS_{epoch_count}_{suffix}')
    
    nlp.to_disk(f'models/{dt_string}_EPOCHS_{epoch_count}_{suffix}')
    print(f'saved model to models/{dt_string}_EPOCHS_{epoch_count}_{suffix}')

    return MODEL_PATH

        
def identify_stations(text, testing=False, MODEL_PATH=None, serve=False, return_doc=False):
    if MODEL_PATH == None:
        return print('Please add a model_path')
    
    nlp.from_disk(MODEL_PATH)
    match = nlp(text)
    matches = []
    for ent in match.ents:
        if testing == True:
            matches.append(ent.label_)
        else:
            matches.append(ent)
            
    if serve == True:
        displacy.serve(match, 'ent', auto_select_port=True)
    if return_doc == True:
        return match
    
    return matches


def testANNOTS(DATASET=TEST_DATA, MODEL_PATH=None):
    if MODEL_PATH == None:
        return print('Please add a model_path')
    tagCount = 0
    correctCount = 0
    for dataset in DATASET:
        for data in dataset:
            test = []
            if type(data) == str:
              print(f"Message: {data}")
              test_message = identify_stations(data, testing=True)
        
            if type(data) == dict:
              for item in data['entities']:
                  tagCount += 1
                  if item[2] in test_message:
                      correctCount += 1
          
    print(f"\nResult: {correctCount/tagCount} Tags: {tagCount} Correct annots: {correctCount}" )

def testMessages(DATASET='data/messages.txt', MODEL_PATH=None):
    if MODEL_PATH == None:
        return print('Please add a model_path')
    with open(DATASET) as file:
        messages = file.read().split('\n')

    docs = []
    for message in messages:
        matches = identify_stations(message, MODEL_PATH=MODEL_PATH, return_doc=True)
        docs.append(matches)

    displacy.serve(docs, style='ent', auto_select_port=True)

