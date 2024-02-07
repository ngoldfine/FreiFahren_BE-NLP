
# flake8: noqa
import spacy
from spacy.training import Example
from spacy import displacy
from data.ANNOTATED_MESSAGES_LSTM import ANNOTATED_DATA
from data_parser import TRAIN_DATA, patterns_for_match
from datetime import datetime
import os
import random

# TODO: create a Model class, or maybe utils/tools and separate everything, so we can easily and intuitively create models and test them


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


    def train(self, EPOCHS=5, until_loss=1, DATASET=TRAIN_DATA):
        # Assuming TRAIN_DATA is a list of tuples, each containing a text and a dictionary of annotations
        examples = [Example.from_dict(self.nlp.make_doc(text), annotations) for text, annotations in DATASET]

        epoch_count = 0

        # Train the model
        optimizer = self.nlp.initialize()

        for itn in range(EPOCHS):
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
    

    def identify_stations(self, text, testing=False, serve=False, return_doc=False):
        
        match = self.nlp(text)
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



M1 = Model('models/06-02-2024___17.26.46')




# from spacy.matcher import Matcher
# from spacy.tokens import Span, Doc
# import spacy

# # Process a document
# doc = M1.nlp("Mon2 Blauwesten gerade in der U8, sind Voltastrss. drin geblieben. Richtung Wittenau.Jetzt noch 2 andere ohne Westen an der U8 Pankstr.")



# words = []
# tags = []
# for ent in doc.ents:
#     words.append(ent.text)
#     tags.append(ent.label_)
# doc = Doc(M1.nlp.vocab, words=words, ents=doc.ents, tags=tags)

# for token in doc:
#     print(token.text, token.ent_type_)
# # Add the Matcher with station patterns
# matcher = Matcher(M1.nlp.vocab)

# for patterns in patterns_for_match:
#     matcher.add(patterns[0], [patterns[1]])


# matches = matcher(doc)

# for match_id, start, end in matches:
#     string_id = M1.nlp.vocab.strings[match_id]  # Get string representation
#     span = doc[start:end]  # The matched span
#     print(string_id, 'test', span)



