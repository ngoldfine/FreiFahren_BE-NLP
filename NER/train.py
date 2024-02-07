# flake8: noqa

import spacy
from spacy import displacy
import random
import os
from datetime import datetime
from spacy.training import Example
from data_parser import TRAIN_DATA
from ner_lstm import nlp

ner = nlp.get_pipe('ner')

# Add your specific labels to the NER component
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])


def train(nlp, EPOCHS=5, until_loss=10, DATASET=TRAIN_DATA, suffix=""):
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
