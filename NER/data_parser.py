# flake8: noqa

from data.ANNOTATED_MESSAGES_LSTM import ANNOTATED_DATA
import json
import re

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


# GETTING ALL THE SYNONYMS for the NER
with open('data/data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

for station in data['sBahn_stations_with_synomyms']:
    for synonyms in data['sBahn_stations_with_synomyms'][f'{station}']:
        TRAIN_DATA.append([synonyms, {'entities': [[0, len(synonyms), "STATION"]]}])

for station in data['uBahn_stations_with_synomyms']:
    for synonyms in data['uBahn_stations_with_synomyms'][f'{station}']:
        TRAIN_DATA.append([synonyms, {'entities': [[0, len(synonyms), "STATION"]]}])

# GETTING ALL FOR THE MATCHER

patterns_for_match = []


for station in data['sBahn_stations_with_synomyms']:
    for synonyms in data['sBahn_stations_with_synomyms'][f'{station}']:
        patterns_for_match.append([f'{station}', [{'LOWER' : { 'FUZZY1': synonyms.lower() } }]])
        
    

for station in data['uBahn_stations_with_synomyms']:
    for synonyms in data['uBahn_stations_with_synomyms'][f'{station}']:
        patterns_for_match.append([f'{station}', [{'LOWER' : { 'FUZZY1': synonyms.lower() } }]])
        

# GETTING ALL THE FORMAL LINES AND STATIONS
with open('data/stations_and_lines.json', 'r', encoding='utf-8') as file:
   stations_and_lines = json.load(file)

for lines in stations_and_lines:
  for station in stations_and_lines[f'{lines}']:
    TRAIN_DATA.append([station, {"entities": [[0, len(station), "STATION"]]}])  


for lines in stations_and_lines:
  for station in stations_and_lines[f'{lines}']:
        patterns_for_match.append([f'{station}', [{'LOWER' : { 'FUZZY1': station.lower() } }]])
        

# import spacy
# from spacy.tokens import DocBin

# nlp = spacy.load('models/epoch10')

# # the DocBin will store the example documents
# count = 0

# db = DocBin()
# for text, annotations in TRAIN_DATA:
#     doc = nlp(text)
#     ents = []
#     for start, end, label in annotations['entities']:
#         span = doc.char_span(start, end, label=label)
#         ents.append(span)
    
#     if doc.text != "":
#        doc.ents = ents
#     else:
#        doc.ents = []
    
#     db.add(doc)
#     if count == len(TRAIN_DATA)/2:
#        break
#     else:
#        count += 1
# db.to_disk("./train.spacy")


# count = len(TRAIN_DATA)/2

# db = DocBin()
# for text, annotations in TRAIN_DATA:
#     doc = nlp(text)
#     ents = []
#     for start, end, label in annotations['entities']:
#         span = doc.char_span(start, end, label=label)
#         ents.append(span)
    
#     if doc.text != "":
#        doc.ents = ents
#     else:
#        doc.ents = []
    
#     db.add(doc)
#     if count == len(TRAIN_DATA):
#        break
#     else:
#        count += 1
# db.to_disk("./dev.spacy")