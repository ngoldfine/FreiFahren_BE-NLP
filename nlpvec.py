from hdclib import generate_random_vector
from hdclib import shift, bind, bundle, normalize, cosine_similarity
import os
import json
import random 
import numpy as np
from test_cases import test_cases

# SETTINGS 

N = 10000

DIRECTORY = "hypervector"

with open('stations_and_lines.json', 'r') as f:
    data = json.load(f)
    f.close()
lines = []

for line in data:
    lines.append(line)


def encodeAlphabet():
    vars = {}

    # from a to z and space using ascii code
    # from a to z, A to Z, and special characters using ascii code
    for letter in list(map(chr, range(ord('a'), ord('z')+1))) + list(map(chr, range(ord('A'), ord('Z')+1))) + ['ö', 'ä', 'ü', 'ß', '.', '-', '(', ')', '/'] + list(map(str, range(0, 10))):        
        vars[letter] = generate_random_vector(N, empty=False)


    vars[' '] = generate_random_vector(N)
    
    alphabet = np.array(list(vars.values()))

    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)
    np.savetxt(f'{DIRECTORY}/alphabet.txt', alphabet, fmt='%f')

    print("saved alphabet to alphabet.txt")

    return vars


def loadAlphabet():
    alphabet = np.loadtxt(f'{DIRECTORY}/alphabet.txt')
    vars = {}
    i = 0
    for letter in list(map(chr, range(ord('a'), ord('z')+1))) + list(map(chr, range(ord('A'), ord('Z')+1))) + ['ö', 'ä', 'ü', 'ß', '.', '-', '(', ')', '/'] + list(map(str, range(0, 10))):        
       
        vars[letter] = alphabet[i]
        i += 1

    vars[' '] = alphabet[i]

    return vars


def encodeSample(file_path, num_words=None):
    vars = loadAlphabet()
    
    language = generate_random_vector(N, empty=True)
    word_count = 0

    


    with open(file_path, 'r') as file:
        text = file.read().replace('\n', '').lower()
        words = text.split()
        progress = 0

        for word in words:

            if num_words is not None and word_count >= num_words:
                break

            for i in range(len(word) - 2):
                trigram = word[i:i+3]

                # THE = rr(T)×r(H)×E
                first = shift(vars[trigram[0]], 2)
                second = shift(vars[trigram[1]], 1)
                third = vars[trigram[2]]
                
                
                trigramSum = bind(first, second)
                trigramSum = bind(trigramSum, third)

                language = bundle([language, trigramSum])

            word_count += 1
            progress += 1
            print(f"progress of {file_path}: " + str(progress) + "/" + str(len(words)))
            
    print("done encoding " + file_path)
    
    return normalize(language)


def encodeMessage(message, num_words=None):
    vars = loadAlphabet()
    
    language = generate_random_vector(N, empty=True)
    word_count = 0

    text = message.replace('\n', '').replace('/', '--').lower()
    words = text.split()

    for word in words:

        if num_words is not None and word_count >= num_words:
            break

        for i in range(len(word) - 2):
            trigram = word[i:i+3]

            # THE = rr(T)×r(H)×E
            # Überprüfen, ob character was von a-z, A-Z, ä-ö, Ä-Ö, 1-9 und . - drinne hat. (Emojis bspw. werden übersprungen)
            if trigram[0] in vars:
                first = shift(vars[trigram[0]], 2)
            else:
                continue

            if trigram[1] in vars:
                second = shift(vars[trigram[1]], 1)
            else:
                continue

            if trigram[2] in vars:
                third = vars[trigram[2]]
            else:
                continue
            
            
            trigramSum = bind(first, second)
            trigramSum = bind(trigramSum, third)

            language = bundle([language, trigramSum])

        word_count += 1
        
    
    return normalize(language)


def encodeStations():
    vars = loadAlphabet()

    with open('stations_and_lines.json', 'r') as file:
        data = json.load(file)

    for line in range(0,25):
        print(f"Encoding line {line+1}")
        for station in data[lines[line]]:

            station_vec = generate_random_vector(N, empty=True)

            station = station.replace('/', '--')
            for i in range(len(station) - 2):
                trigram = station[i:i+3]

                # THE = rr(T)×r(H)×E
                first = shift(vars[trigram[0]], 2)
                second = shift(vars[trigram[1]], 1)
                third = vars[trigram[2]]
                
                trigramSum = bind(first, second)
                trigramSum = bind(trigramSum, third)

                station_vec = bundle([station_vec, trigramSum])
            
            norm_stations = normalize(station_vec)

            if not os.path.exists(f"{DIRECTORY}/{lines[line]}"):
                os.makedirs(f"{DIRECTORY}/{lines[line]}")

            np.savetxt(f"{DIRECTORY}/{lines[line]}/{station}.txt",
                       norm_stations, fmt='%f')
            print(f"Saved: {station}")


def findStationVec(message):
    message_encoded = encodeMessage(message)
    with open('stations_and_lines.json', 'r') as file:
        dataStations = json.load(file)

        nearest_station = 0.0
        station_name = ""

        for line in range(0, 25):
            
            for station in dataStations[f'{lines[line]}']:

                station = station.replace('/', '--')
                PATH = f'{DIRECTORY}/{lines[line]}/{station}.txt'
                station_tmp = np.loadtxt(PATH)

                similarity = cosine_similarity(message_encoded, station_tmp)
                if (nearest_station < similarity):
                    nearest_station = similarity
                    station_name = station
                
    if nearest_station < 0.40:
        station_name = None
    return [station_name, nearest_station]




def test():
    random.shuffle(test_cases)
    correct = 0

    for test in test_cases:
        message = test[0]
        prediction = findStationVec(message)
        
        if (test[1] == prediction[0]):
            correct += 1
            print("\n Correct: ")
        else:
            print("\n False: ")
        
        print(f"Message:    {message} ")
        print(f"Predicted:  {prediction[0]}")
        print(f"Similarity: {prediction[1]}")
        print(f"Expected:   {test[1]}")
        print("")
 
    accuracy = correct/len(test_cases)

    print(f"Accuracy: {accuracy}")

test()