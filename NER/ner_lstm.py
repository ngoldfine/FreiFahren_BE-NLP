
# flake8: noqa
import spacy
from spacy.training import Example
from spacy import displacy
from spacy.tokens import Doc
from data.ANNOTATED_MESSAGES_LSTM import ANNOTATED_DATA
from datetime import datetime
import os
import random

import sys
import os

# So we can import data_parser.py based on the current directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

# Add the current directory to sys.path
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir)

from data_parser import TRAIN_DATA, patterns_for_match


class Model:
    def __init__(self, model_path = None):
        self.model_path = model_path

        if self.model_path is None:
            self.nlp = spacy.blank('de')
            self.ner = self.nlp.create_pipe('ner')
            self.nlp.add_pipe('ner')

            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y___%H.%M.%S")
            self.model_path = f'models/{dt_string}'

            print(f'new blank \'de\' model loaded in {self.model_path}')
        else:
            self.nlp = spacy.load(f"{self.model_path}")
            self.ner = self.nlp.get_pipe('ner')

            print(f'model from {self.model_path} loaded')


    def train(self, epochs=5, until_loss=1, dataset=TRAIN_DATA):
        # Assuming TRAIN_DATA is a list of tuples, each containing a text and a dictionary of annotations
        examples = [Example.from_dict(self.nlp.make_doc(text), annotations) for text, annotations in dataset]

        epoch_count = 0

        # Train the model
        optimizer = self.nlp.initialize()

        for itn in range(epochs):
            random.shuffle(examples)
            losses = {}

            for example in examples:
                self.nlp.update([example], sgd=optimizer, drop=0.35, losses=losses)
            
            if losses['ner'] < until_loss:
                print("stopping at: ", losses)
                break
            epoch_count +=1

            print(losses)

        if not os.path.exists(f'{self.model_path}'):
            os.makedirs(f'{self.model_path}')
        
        self.nlp.to_disk(f'{self.model_path}')
        print(f'saved model to {self.model_path}')
    

    def identify_stations(self, text, testing=False, return_doc=False):
        
        match = self.nlp(text)
        matches = []
        for ent in match.ents:
            if testing == True:
                matches.append(ent.label_)
            else:
                matches.append(ent)
                
        if return_doc == True:
            return match
        
        return matches

    def text(self, text):

        doc = self.nlp(text)
        ents = []
        words = []
        tags = []

        for ent in doc.ents:
            ents.append(ent)
            words.append(ent.text)
            tags.append(ent.label_)

        newDoc = Doc(self.nlp.vocab, words=words, ents=ents, tags=tags)
        return newDoc.text

    def get_one_station(self, text):
        doc = self.nlp(text)
        
        for ent in doc.ents:
            if ent.label_ == 'STATION':
                return ent.text
        
    
    def get_line(self, text):
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == 'LINE':
                return ent.text
        
    def get_direction(self, text):
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == 'DIRECTION':
                return ent.text
    

M1 = Model('NER/models/loss17')
