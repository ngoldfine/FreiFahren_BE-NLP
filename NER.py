import spacy
from spacy.util import minibatch, compounding
from spacy.training import Example
import random

# Hier definieren wir die Trainingsdaten
TRAIN_DATA = [
    ("U6 Mehringdamm -> hallesches Tor gerade ausgestiegen. 2 Kontrolleure in schwarz, glaube ich. :", 
        {"entities": [ (0, 2, "LINE"), (3, 14, "DIRECTION"), (18, 32, "STATION")]}),
    ("S Alexanderplatz west direction at least one ticket checker with a white puffer jacket on the platform", 
        {"entities": [ (2, 16, "STATION")]}),
    ("u6 leopoldplatz towards alt mariendorf 2 people with 2 cops",
        {"entities": [ (0, 2, "LINE"), (3, 15, "STATION"), (24, 38, "DIRECTION")]}),
    # TODO: MEHR DATEN!!!!
]

# Hier laden wir eine weisse Leinwand mit der deutschen Sprache,
# d.h. ISO ist auf deutsch, und basic components fuer die Prozessierung der Sprache
nlp = spacy.blank("de")

# Die Pipeline startet mit einem Named-Entity-Recognizer (Nutzt auch Vector-Model, denke ich)
# Dazu koennen wir auch noch weitere Pipes/eigene Komponenten hinzufuegen, indem wir nlp.add_pipe(<FUNKTION>) verwenden
ner = nlp.add_pipe("ner")

# Hier fuegen wir die labels hinzu, die wir trainieren wollen
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Hier starten wir das Training
nlp.begin_training()

# 200 Trainingsepochen
for itn in range(200):
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
    print(f"Loss at iteration {itn} - {losses}")

# Basic Testing. Kann gut funktionieren, wenn wir genug Trainingsdaten haben
TEST_DATA = [
        ("Gerade S Tiergarten Richtung alt mariendorf",
         {"entities": [(9, 19, "STATION"), (29, 43, "DIRECTION")]}),
]

# Hier testen wir das Model
for text, annots in TEST_DATA:
    doc = nlp(text)
    print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
    print("Expected", [(text[start:end], label) for start, end, label in annots["entities"]])

#TODO: Schreibe alle Linien auf, wie z.B. U6 Platz der Luftbruecke, um die Direction zu bestimmen
    # mit diesen Informationen koennen wir sicherlich einfacher die Infos bestimmen, also das NER
    # muss nur nach diesen Worten suchen und dann die Stationen bestimmen
doc = nlp("U6 Hallesches Tor -> Mehringdam gerade ausgestiegen. 2 Kontrolleure in schwarz, glaube ich. :")

print("Entities", [(ent.text, ent.label_) for ent in doc.ents])