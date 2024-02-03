# A ChatGPT Query that is supposed to label the data. The message is inputted to the model and the output is the station, line, and direction.
# The input messages are taken from messages_and_times.json and the output is supposed to be saved as a csv file.

import json
import requests


def get_input_messages():
    with open('messages_and_times.json', 'r') as f:
        messages = json.load(f)
    # traverse through the messages to get the text
    input_messages = [message['message'] for message in messages]
    return input_messages


if __name__ == "__main__":
    input_messages = get_input_messages()
    print(input_messages)