import spacy
from spacy.util import minibatch, compounding
from spacy.training import Example
from spacy import displacy

import json
import random



with open('data/stations_and_lines.json', 'r') as file:
    stations_and_lines = json.load(file)

# Hier definieren wir die Trainingsdaten
TRAIN_DATA = [
    ('U6 Mehringdamm -> hallesches Tor gerade ausgestiegen. 2 Kontrolleure in schwarz, glaube ich. :', 
        {'entities': [ (0, 2, 'LINE'), (3, 14, 'STATION'), (18, 32, 'STATION')]}),
    ('S Alexanderplatz west direction at least one ticket checker with a white puffer jacket on the platform', 
        {'entities': [ (2, 16, 'STATION')]}),
    ('u6 leopoldplatz towards alt mariendorf 2 people with 2 cops',
        {'entities': [ (0, 2, 'LINE'), (3, 15, 'STATION'), (24, 38, 'STATION')]}),
    ('Gerade S Tiergarten Richtung alt mariendorf',
        {'entities': [(9, 19, 'STATION'), (29, 43, 'STATION')]}),
    ('s-bahn kontrolleure friedrichstrasse 2mal weiblich eine kräftig und blonde haare lang andere dünner grüne jacke',
        {'entities': [[20,36,'STATION']]}),
    ('4 Kontrolleur*innen S85 nach Buch',
        {'entities': [[20,23,'LINE'],[29,33,'STATION']]}),
    ('Sind nicht zu übersehen 😅',
        {'entities': []}),
    ('U5 nach Hönow',
        {'entities':[[0,2,'LINE'],[8,13,'STATION']]}),
    ('Blaue veste',
        {'entities':[]}),
    ('S42 grade landsbergeralee los',
        {'entities':[[0,3,'LINE'],[10,25,'STATION']]}),
    ('froilein rattenmeier sie/shehey kurze frage: der kontroletti hat meinen namen falsch geschrieben, adresse stimmt aber. kann das ...Wenn deine Ausweisnummer stimmt finden die dich überall in der EU außer in Rumänien 😬',
        {'entities':[]}),
    ('FlinnUnd wenn er den Namen hat aber nicht die Adresse?Die Ausweisnummer bzw das Personaldokument worüber sie dich aufgenommen haben ist entscheidend',
        {'entities':[]}),
    ('zwei bos westen mit gelbem nacken sind gerade schönleinstr u8 richtung hermannstr eingestiegen',
        {'entities':[[46,58,'STATION'],[59,61,'LINE'],[71,81,'STATION']]}),
    ('3 bos u8 richtung wittenau, weinmeisterstr ausgestiegen',
        {'entities':[[6,8,'LINE'],[18,26,'STATION'],[28,42,'STATION']]}),
    ('Große Kontrolle beim aussteigen an der U-Alt-Tempelhof U6',
        {'entities':[[39,54,'STATION'],[55,57,'LINE']]}),
    ('Ring, tempelhof, richtung sudkreuz',
        {'entities':[[6,15,'STATION'],[26,34,'STATION']]}),
    ('u8 Voltastr.',
        {'entities':[[0,2,'LINE'],[3,11,'STATION']]}),
    ('mind. 2 blaue westen am leopoldplatz, polizei ist auch da, am u9 gleis',
        {'entities':[[24,36,'STATION'],[62,64,'LINE']]}),
    ('Neukölln  sbahn 2 männlich gelesene'
        ,{'entities':[[0,8,'STATION']]}),
    ('Lazi ♀️Neukölln  sbahn 2 männlich geleseneBeide glatze',
        {'entities':[[5,15,'STATION']]}),
    ('Jetzt noch zusätzlich zwei weitere steigen von s41 aus in Tempelhof',
        {'entities':[[47,50,'LINE'],[58,67,'STATION']]}),
    ('2 Männer mit blauen Westen stiegen in die U8 Richtung Witteneu @ Henrich-Heine-Straße ein',
        {'entities':[[42,44,'LINE'],[54,62,'STATION'],[65,85,'STATION']]}),
    ('S7 Richtung potsdam Hbf, 3 w gelesen, gleich griebnitzsee',
        {'entities':[[0,2,'LINE'],[12,23,'STATION'],[45,57,'STATION']]})
    
    # TODO: MEHR DATEN!!!!
]

# # Add the station names to your data
# for lines in stations_and_lines:
#     for station in stations_and_lines[lines]:
#         TRAIN_DATA.append((station, {'entities': [(0, len(station), 'STATION')]}))
#         print((station, {'entities': [(0, len(station), 'STATION')]}))
#         print(f'Added entity: {station}')


# print(TRAIN_DATA)

# Hier laden wir eine weisse Leinwand mit der deutschen Sprache,
# d.h. ISO ist auf deutsch, und basic components fuer die Prozessierung der Sprache
nlp = spacy.blank('de')

# Die Pipeline startet mit einem Named-Entity-Recognizer (Nutzt auch Vector-Model, denke ich)
# Dazu koennen wir auch noch weitere Pipes/eigene Komponenten hinzufuegen, indem wir nlp.add_pipe(<FUNKTION>) verwenden
ner = nlp.add_pipe('ner')

# Hier fuegen wir die labels hinzu, die wir trainieren wollen
for _, annotations in TRAIN_DATA:
    for ent in annotations.get('entities'):
        ner.add_label(ent[2])

# Hier starten wir das Training
nlp.begin_training()

# 200 Trainingsepochen
for itn in range(20):
    # Shufflen der Trainingsdaten
    random.shuffle(TRAIN_DATA)
    losses = {}

    # Hier geben wir die Trainingsbatches ein
    # Wir nutzen wir Minibatches um kleine Teile der Trainingsdaten zu trainieren
    # und die Funktion compounding um steigend mehr Daten zu trainieren, das ist besser als einfach nur 1 Batch zu trainieren
    for batch in minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001)):
        examples = []
        for text, annots in batch:
            # Create an Example object
            example = Example.from_dict(nlp.make_doc(text), annots)
            examples.append(example)
        
        # Hier trainieren wir das Model mit den Beispielen
        # und speichern die Losses
        # nlp.update() ist eine Methode, die das Model trainiert
        # und die Losses zurueckgibt
        nlp.update(examples, losses=losses)
    print(f'Loss at iteration {itn} - {losses}')

nlp.to_disk('models/ner_model')


#TODO: Schreibe alle Linien auf, wie z.B. U6 Platz der Luftbruecke, um die Direction zu bestimmen
    # mit diesen Informationen koennen wir sicherlich einfacher die Infos bestimmen, also das NER
    # muss nur nach diesen Worten suchen und dann die Stationen bestimmen
doc = nlp('mehringdamm platz der luftbruecke u6 richtung alt mariendorf 2 kontrolleure in schwarz, glaube ich. :')

# displacy.render(doc, style='ent')
options = {'ents': ['STATION', 'LINE'], 'colors': {'STATION': 'lightgreen', 'LINE': 'lightblue'}}
detected_stations = []

for ent in doc.ents:
    if ent.label_ == 'STATION':
        detected_stations.append(ent.text)
        print(ent.text, ent.label_)

print(detected_stations)


