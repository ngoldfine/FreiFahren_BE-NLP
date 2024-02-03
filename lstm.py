from sklearn.preprocessing import LabelEncoder
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Convolution1D

from test_cases import test_cases
import numpy as np

data = test_cases

# Separate the dataset into texts and their corresponding labels
texts = [item[0] for item in data]

# Prepare labels
# For the labels, we will combine the three pieces of information into a single string
# This is because we are treating this as a multi-class classification problem
# Each unique combination of (direction, line, station) will be treated as a separate class
labels = [f"{item[1] or 'None'} {item[2] or 'None'} {item[3] or 'None'}".strip() for item in data]


# Tokenize text
tokenizer = Tokenizer(num_words=1000, oov_token="<OOV>")
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
padded_sequences = pad_sequences(sequences, maxlen=20, padding='post')

label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(labels)

model = Sequential([
    Embedding(1000, 64, input_length=20),
    LSTM(64),
    Dense(64, activation='relu'),
    Dense(len(set(encoded_labels)), activation='softmax')
])

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Split the data
X_train, X_test, y_train, y_test = train_test_split(padded_sequences, encoded_labels, test_size=0.2)

# Train the model
model.fit(X_train, y_train, epochs=250, validation_data=(X_test, y_test))

new_texts = ["Gerade maennlich gelesen, U6 Richtung Alt-Mariendorf, in Platz der Luftbrucke "]
new_sequences = tokenizer.texts_to_sequences(new_texts)
new_padded = pad_sequences(new_sequences, maxlen=20, padding='post')

predictions = model.predict(new_padded)
predicted_label_indices = np.argmax(predictions, axis=1)
predicted_labels = label_encoder.inverse_transform(predicted_label_indices)

print(predicted_labels)


   