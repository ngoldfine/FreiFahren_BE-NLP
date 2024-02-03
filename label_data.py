import json
import csv
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)


def get_input_messages():
    with open('messages_and_times.json', 'r') as f:
        messages = json.load(f)
    input_messages = [message['message'] for message in messages]
    return input_messages


def label_data(messages):
    labeled_data = []
    for message in messages[:5]:  # Only label the first 5 messages for testing
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Your task is to label the given data with station, line, and direction."},
                    {"role": "user", "content": message}
                ],
                temperature=0.25
            )
            labeled_data.append(response.choices[0].message.content)
        except Exception as e:
            print(f"An error occurred: {e}")
            labeled_data.append("Error processing message")
    return labeled_data


def save_to_csv(labeled_data):
    with open('labeled_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Message", "Label"])
        for label in labeled_data:
            writer.writerow([label])


if __name__ == "__main__":
    input_messages = get_input_messages()
    labeled_data = label_data(input_messages)
    save_to_csv(labeled_data)
