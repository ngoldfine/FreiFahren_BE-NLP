# flake8: noqa
from data_parser import TEST_DATA
from ner_lstm import Model
from spacy import displacy

def testANNOTS(MODEL: Model, DATASET=TEST_DATA ):
    tagCount = 0
    correctCount = 0
    for dataset in DATASET:
        for data in dataset:
            if type(data) == str:
              print(f"Message: {data}")
              test_message = Model.identify_stations(data, testing=True)
        
            if type(data) == dict:
              for item in data['entities']:
                tagCount += 1
                if item[2] in test_message:
                    correctCount += 1
                
          
    print(f"\nResult: {correctCount/tagCount} Tags: {tagCount} Correct annots: {correctCount}" )


def testMessages(Model: Model, DATASET='data/messages.txt'):
    colors = {'LINE': '#F67DE3',
          'STATION': '#7DF6D9'}
    options = {'colors': colors}

    with open(DATASET) as file:
        messages = file.read().split('\n')

    docs = []
    for message in messages:
        matches = Model.identify_stations(message, return_doc=True)
        docs.append(matches)

    displacy.serve(docs, style='ent', auto_select_port=True, options=options)

M1 = Model('NER/models/model-best')
testMessages(M1)