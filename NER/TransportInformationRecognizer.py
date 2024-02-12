import spacy
from spacy.tokens import Doc

# NER = Named Entity Recognition
# This class is used to recognize stations (also lines and direction) in a text message


class TransportInformationRecognizer:
    def __init__(self, model_path='NER/models/loss17'):
        self.model_path = model_path
        
        self.nlp = spacy.load(f'{self.model_path}')
        self.ner = self.nlp.get_pipe('ner')

        print(f'model {self.model_path} loaded')

    # input: text message (string)
    # return: a list of all recognized stations in the text
    def get_recognized_stations(self, text: str) -> list:
        
        match = self.nlp(text)
        matches = []
        for entity in match.ents:
            if entity.label_ == 'STATION':
                matches.append(entity)
            
        return matches

    # input: text message (string)
    # return: a text message with only the recognized stations
    def process_text(self, text: str) -> str:

        doc = self.nlp(text)
        entities = []
        words = []
        tags = []

        for entity in doc.ents:
            entities.append(entity)
            words.append(entity.text)
            tags.append(entity.label_)

        new_doc = Doc(self.nlp.vocab, words=words, entities=entities, tags=tags)
        return new_doc.text
    

TextProcessor = TransportInformationRecognizer('NER/models/loss17')

processed_text = TextProcessor.process_text('u2 jetzt zoo')

print(processed_text)