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
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Your task is to label the given data with station, line, and direction."},
                    {"role": "user", "content": f"""
                    I will give you the message and you will have to label it. The format should be like this: 
                    Direction: "example direction",
                    Line: "example line",
                    Station: "example station",

                    Now, here is the message:
                    {message}"""}
                ],
                temperature=0.25
            )
            # Parse the response to extract station, line, and direction
            content = response.choices[0].message.content
            print("API reponse: ", content)
            parsed_data = parse_response(content)
            print("Parsed data: ", parsed_data)
            labeled_data.append(parsed_data)
        except Exception as e:
            print(f"An error occurred: {e}")
            labeled_data.append({"Station": "Error", "Line": "Error", "Direction": "Error"})
    return labeled_data


def parse_response(content):
    # Initialize default values in case some information is missing
    parsed_data = {"Station": "", "Line": "", "Direction": ""}
    lines = content.split('\n')
    for line in lines:
        if "Direction:" in line:
            parsed_data["Direction"] = line.split('"')[1]
        elif "Line:" in line:
            parsed_data["Line"] = line.split('"')[1]
        elif "Station:" in line:
            parsed_data["Station"] = line.split('"')[1]
    return parsed_data


def save_to_csv(labeled_data, input_messages):
    with open('labeled_messages.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Input Message", "Station", "Line", "Direction"])
        writer.writeheader()
        for i, data in enumerate(labeled_data):
            row = {"Input Message": input_messages[i], **data}
            writer.writerow(row)


if __name__ == "__main__":
    input_messages = get_input_messages()
    labeled_data = label_data(input_messages)
    save_to_csv(labeled_data, input_messages)
