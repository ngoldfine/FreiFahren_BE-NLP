import json
import pickle
import os
import random
import string

data = []

# Load the messages from the JSON file
with open('messages_and_times.json', 'r') as f:
    messages = json.load(f)

# Iterate over the messages
for message in messages:
    print("Message:", message["message"])

    current_station = input("Enter the current station for this message (or quit): ")
    if current_station.lower() == 'quit':
        break
    
    if current_station.lower() == "none" or current_station.lower() == "":
        current_station = None

    print()

    line = input("Enter the line for this message: ")

    if line.lower() == "none" or line.lower() ==  "":
        line = None

    print()
    direction = input("Enter the direction for this message: ")

    if direction.lower() == "none" or direction.lower() == "":
        direction = None

    data.append((message["message"], current_station, line, direction))

# Generate a random filename
filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

# Ensure the directory exists
os.makedirs('labeled_data', exist_ok=True)

# Save the data
with open(os.path.join('labeled_data', filename + '.pkl'), 'wb') as f:
    pickle.dump(data, f)