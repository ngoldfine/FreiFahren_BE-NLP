
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
            self.ner = self.nlp.get_pipe('spancat')

            print(f'model from {self.model_path} loaded')

    def text(self, text):
        doc = self.nlp(text)
        print("from spancat.py")
        text = ""
        for span in doc.spans['sc']:
            text = text + " " + span.text
        if text == "":
            return None
        else:
            return text
        
    # def get_one_station(self, text):
    #     doc = self.nlp(text)
    #     print("from spancat.py")
    #     text = ""
    #     for span in doc.spans['sc']:
    #         if span.label_ == "station":
    #             text = text + " " + str(span.text)
    #     if text == "":
    #         return None
    #     else:
    #         return text
        
    def check_overlap(self, spans):
        for i in range(len(spans)):
            for j in range(i+1, len(spans)):
               if spans[i].start > spans[j].start and spans[i].end == spans[j].end:
                   return spans[i].text
        return None

    
    def getStationOverlap(self, text):
        doc = self.nlp(text)
        spans = []
        for span in doc.spans['sc']:
            if span.label_ == "DIRECTION" or span.label_ == "STATION":
                spans.append(span)
        
        for i in range(len(spans)):
            for j in range(i+1, len(spans)):
                if spans[i].text not in spans[j].text:
                    return spans[i].text
                
    def getStation(self, text):
        doc = self.nlp(text)
        spans = []
        for span in doc.spans['sc']:
            if span.label_ == "STATION":
                return span.text
        
    def getDirection(self, text):
        doc = self.nlp(text)
        spans = []
        for span in doc.spans['sc']:
            if span.label_ == "DIRECTION" or span.label_ == "LINE" or span.label_ == "STATION":
                spans.append(span)
        
        for i in range(len(spans)):
            for j in range(i+1, len(spans)):
                if spans[i].text in spans[j].text:
                    return spans[i].text
        

    def getLine(self, text):
        doc = self.nlp(text)
        spans = []
        for span in doc.spans['sc']:
            if span.label_ == "LINE":
                if span.text != "S-":
                    return span.text
    
        

    def serve(self ,text):
        doc = self.nlp(text)
        
        displacy.serve(doc, style="span", auto_select_port=True)


        

M2 = Model('NER/models/spancat-best')

txt = M2.serve("U8 Rosi Richtung Hermannstrasse ")

