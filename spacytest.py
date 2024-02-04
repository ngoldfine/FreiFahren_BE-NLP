import spacy
import pandas as pd
import random

df = pd.read_json('messages.json', orient='records', encoding='ISO-8859-1')

messages = [_ for _ in df['message']]




print(random.choices(messages, k=5))